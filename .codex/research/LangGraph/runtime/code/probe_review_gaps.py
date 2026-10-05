"""Offline counterexamples added during the full study-note review."""
import json
from importlib.metadata import version
from operator import add
from typing import Annotated

from typing_extensions import TypedDict
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import CachePolicy


class JoinState(TypedDict):
    results: Annotated[list[str], add]


def join_run(barrier: bool, unequal: bool = True, missing: bool = False):
    seen = []
    builder = StateGraph(JoinState)
    builder.add_node('a', lambda state: {'results': ['a']})
    builder.add_node('b', lambda state: {'results': ['b']})
    def collect(state):
        seen.append(list(state['results']))
        return {}
    builder.add_node('c', collect)
    builder.add_edge(START, 'a')
    if not missing:
        if unequal:
            builder.add_node('b1', lambda state: {})
            builder.add_edge(START, 'b1')
            builder.add_edge('b1', 'b')
        else:
            builder.add_edge(START, 'b')
    if barrier:
        builder.add_edge(['a', 'b'], 'c')
    else:
        builder.add_edge('a', 'c')
        builder.add_edge('b', 'c')
    builder.add_edge('c', END)
    graph = builder.compile()
    output = graph.invoke({'results': []})
    return {'c_inputs': seen, 'final_results': output['results']}


def probe_join():
    normal = join_run(False)
    barrier = join_run(True)
    assert normal['c_inputs'] == [['a'], ['a', 'b']]
    assert barrier['c_inputs'] == [['a', 'b']]
    return {'separate_edges': normal, 'barrier_edge': barrier}


def probe_same_step():
    normal = join_run(False, unequal=False)
    barrier = join_run(True, unequal=False)
    assert normal['c_inputs'] == barrier['c_inputs'] == [['a', 'b']]
    return {'separate_edges': normal, 'barrier_edge': barrier}


def probe_missing_signal():
    result = join_run(True, missing=True)
    assert result == {'c_inputs': [], 'final_results': ['a']}
    return result


class Question(TypedDict):
    question: str


class CacheState(Question):
    log: Annotated[list[str], add]


def probe_cached_control_writes():
    counts = {'work': 0, 'route': 0, 'next': 0}
    def work(state: Question):
        counts['work'] += 1
        return {'log': ['work']}
    def route(state):
        counts['route'] += 1
        return 'next'
    def next_node(state):
        counts['next'] += 1
        return {}
    builder = StateGraph(CacheState)
    builder.add_node('work', work, cache_policy=CachePolicy())
    builder.add_node('next', next_node)
    builder.add_edge(START, 'work')
    builder.add_conditional_edges('work', route, ['next'])
    builder.add_edge('next', END)
    graph = builder.compile(checkpointer=InMemorySaver(), cache=InMemoryCache())
    config = {'configurable': {'thread_id': 'cache-review'}}
    first = graph.invoke({'question': 'q'}, config)
    second = graph.invoke({'question': 'q'}, config)
    assert first['log'] == ['work']
    assert second['log'] == ['work', 'work']
    assert counts == {'work': 1, 'route': 1, 'next': 2}
    return {'calls': counts, 'first_log': first['log'], 'second_log': second['log']}


def main():
    probes = {'unequal_join': probe_join, 'same_step_join': probe_same_step,
              'missing_barrier_signal': probe_missing_signal,
              'cached_control_writes': probe_cached_control_writes}
    results = {name: {'status': 'passed', 'observed': fn()} for name, fn in probes.items()}
    print(json.dumps({'langgraph_version': version('langgraph'), 'results': results},
                     indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
