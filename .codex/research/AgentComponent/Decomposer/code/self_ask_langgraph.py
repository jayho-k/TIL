"""Self-ask 반복 실행을 LangGraph StateGraph로 구성한다."""
from dataclasses import asdict
import time
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from self_ask import Completion, Evidence, FEW_SHOT, SearchResult, STOP, TransientError, normalize_query, parse_action


class GraphInput(TypedDict):
    question: str


class GraphOutput(TypedDict):
    status: str
    answer: str | None
    transcript: str
    searches: list[dict]
    events: list[dict]
    model_calls: int


class SelfAskState(GraphOutput, total=False):
    question: str
    started: float
    action: str
    value: str
    seen_queries: list[str]


def build_self_ask_graph(complete, search_answer, *, few_shot=FEW_SHOT,
                         max_searches=5, max_model_calls=12, max_retries=1,
                         max_prompt_chars=24000, max_answer_chars=2000,
                         max_seconds=60, require_evidence=True, clock=time.monotonic):
    """컴파일된 그래프 반환. invoke({'question': ...}) 또는 stream()으로 실행.

    기존 Completion/SearchResult 콜백 계약을 유지한다. State의 리스트는
    각 노드가 새 값으로 반환하며, 요청 간 상태를 공유하지 않는다.
    """
    if (min(max_searches, max_model_calls, max_retries) < 0
            or min(max_prompt_chars, max_answer_chars, max_seconds) <= 0):
        raise ValueError('횟수는 0 이상, 크기와 시간 예산은 양수여야 합니다.')

    def expired(state):
        return clock() - state['started'] >= max_seconds

    def guard(state):
        if expired(state):
            return 'time_limit'
        if len(state['transcript']) > max_prompt_chars:
            return 'prompt_limit'
        return None

    def stop(status, **updates):
        return {'status': status, 'answer': None, **updates}

    def initialize(state: SelfAskState):
        prompt = few_shot + 'Question: ' + ' '.join(state['question'].split())
        return {'status': 'running', 'answer': None,
                'transcript': prompt + '\nAre follow up questions needed here:',
                'searches': [], 'events': [], 'seen_queries': [], 'model_calls': 0,
                'started': clock(), 'action': '', 'value': ''}

    def decide(state: SelfAskState):
        if reason := guard(state):
            return stop(reason)
        events, calls = list(state['events']), state['model_calls']
        failure = 'invalid_output'
        for attempt in range(max_retries + 1):
            if expired(state):
                return stop('time_limit', events=events, model_calls=calls)
            if calls >= max_model_calls:
                return stop('model_call_limit', events=events, model_calls=calls)
            calls += 1
            try:
                reply = complete(state['transcript'], stop=STOP)
            except (TimeoutError, ConnectionError, TransientError):
                if expired(state):
                    return stop('time_limit', events=events, model_calls=calls)
                failure = 'model_unavailable'
                events.append({'type': 'model_retry', 'attempt': attempt + 1})
                continue
            if expired(state):
                return stop('time_limit', events=events, model_calls=calls)
            if not isinstance(reply, Completion) or not isinstance(reply.text, str):
                return stop('invalid_completion', events=events, model_calls=calls)
            if reply.finish_reason == 'length':
                failure = 'generation_truncated'
                events.append({'type': failure})
                continue
            if reply.finish_reason != 'stop':
                return stop('invalid_completion', events=events, model_calls=calls)
            try:
                action, value = parse_action(reply.text)
                if len(value) > max_answer_chars:
                    raise ValueError('출력 길이 제한')
            except ValueError:
                failure = 'invalid_output'
                events.append({'type': failure})
                continue
            return {'action': action, 'value': value, 'events': events, 'model_calls': calls}
        return stop(failure, events=events, model_calls=calls)

    def retrieve(state: SelfAskState):
        if reason := guard(state):
            return stop(reason)
        query = state['value']
        key = normalize_query(query)
        if key in state['seen_queries']:
            return stop('duplicate_query')
        if len(state['searches']) >= max_searches:
            return stop('search_limit')
        events = list(state['events'])
        for attempt in range(max_retries + 1):
            if expired(state):
                return stop('time_limit', events=events)
            try:
                result = search_answer(query)
            except (TimeoutError, ConnectionError, TransientError):
                result = SearchResult('timeout')
            if expired(state):
                return stop('time_limit', events=events)
            if not isinstance(result, SearchResult):
                return stop('invalid_search_result', events=events)
            if result.status != 'timeout':
                break
            events.append({'type': 'search_retry', 'query': query, 'attempt': attempt + 1})
        if result.status != 'supported':
            if result.status not in {'no_evidence', 'conflicting_evidence', 'timeout', 'error'}:
                return stop('invalid_search_result', events=events)
            records = state['searches'] + [{'query': query, **asdict(result)}]
            return stop(result.status, searches=records, events=events)
        if (not isinstance(result.answer, str) or not result.answer.strip()
                or not isinstance(result.evidence, (tuple, list)) or not result.evidence
                or any(not isinstance(e, Evidence) or not isinstance(e.source_id, str)
                       or not e.source_id.strip() or not isinstance(e.quote, str)
                       or not e.quote.strip() for e in result.evidence)):
            return stop('invalid_search_result', events=events)
        if len(result.answer) > max_answer_chars:
            return stop('answer_limit', events=events)
        addition = ((' Yes.' if not state['searches'] else '') + '\nFollow up: ' + query
                    + '\nIntermediate answer: ' + ' '.join(result.answer.split()))
        if len(state['transcript'] + addition) > max_prompt_chars:
            return stop('prompt_limit', events=events)
        return {'transcript': state['transcript'] + addition,
                'searches': state['searches'] + [{'query': query, **asdict(result)}],
                'seen_queries': state['seen_queries'] + [key],
                'events': events + [{'type': 'search_completed', 'query': query}]}

    def finalize(state: SelfAskState):
        if reason := guard(state):
            return stop(reason)
        if require_evidence and not state['searches']:
            return stop('unverified_answer')
        addition = (' No.' if not state['searches'] else '') + '\nSo the final answer is: ' + state['value']
        if len(state['transcript'] + addition) > max_prompt_chars:
            return stop('prompt_limit')
        return {'status': 'completed', 'answer': state['value'], 'transcript': state['transcript'] + addition}

    def after_decide(state: SelfAskState):
        if state['status'] != 'running':
            return END
        return 'retrieve' if state['action'] == 'search' else 'finalize'

    def after_retrieve(state: SelfAskState):
        return 'decide' if state['status'] == 'running' else END

    builder = StateGraph(SelfAskState, input_schema=GraphInput, output_schema=GraphOutput)
    builder.add_node('initialize', initialize)
    builder.add_node('decide', decide)
    builder.add_node('retrieve', retrieve)
    builder.add_node('finalize', finalize)
    builder.add_edge(START, 'initialize')
    builder.add_edge('initialize', 'decide')
    builder.add_conditional_edges('decide', after_decide, ['retrieve', 'finalize', END])
    builder.add_conditional_edges('retrieve', after_retrieve, ['decide', END])
    builder.add_edge('finalize', END)
    graph = builder.compile()
    # 검색 수와 그래프 super-step 수는 다르므로 기본 제한 25에 의존하지 않는다.
    return graph.with_config({'recursion_limit': 2 * max_model_calls + max_searches + 4})
