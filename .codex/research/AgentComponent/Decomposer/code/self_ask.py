"""Self-ask 공통 자료형·파서 및 LangGraph 실행 진입점."""
from dataclasses import dataclass
import re
import unicodedata


FEW_SHOT = """Question: 테오도어 해커와 해리 본 왓킨스 중 누가 더 오래 살았는가?
Are follow up questions needed here: Yes.
Follow up: 테오도어 해커는 사망 당시 몇 살이었는가?
Intermediate answer: 테오도어 해커는 사망 당시 65세였다.
Follow up: 해리 본 왓킨스는 사망 당시 몇 살이었는가?
Intermediate answer: 해리 본 왓킨스는 사망 당시 69세였다.
So the final answer is: 해리 본 왓킨스.

"""
MARKER = re.compile(r"^(Follow up|Intermediate answer|So the final answer is)\s*:\s*(.*)$", re.I)
STOP = ["\nIntermediate answer:", "\nIntermediate Answer:", "\nQuestion:"]


@dataclass(frozen=True)
class Completion:
    text: str
    finish_reason: str = "stop"  # stop 또는 length. 어댑터가 종료 사유를 매핑한다.


@dataclass(frozen=True)
class Evidence:
    source_id: str
    quote: str


@dataclass(frozen=True)
class SearchResult:
    status: str  # supported, no_evidence, conflicting_evidence, timeout, error
    answer: str = ""
    evidence: tuple[Evidence, ...] = ()


class TransientError(Exception):
    """어댑터가 일시적 오류(예: HTTP 429/503)를 변환해 전달하는 예외."""


def parse_action(text):
    """행 시작의 표식만 해석하며 모델이 생성한 중간 답은 버린다."""
    records = []
    in_intermediate = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = MARKER.fullmatch(line)
        if match:
            kind = match[1].lower()
            records.append((kind, match[2].strip()))
            in_intermediate = kind == "intermediate answer"
        elif line.lower() not in {"yes.", "no.", "yes", "no"} and not in_intermediate:
            raise ValueError("예상하지 못한 출력 행")
    follow = [value for kind, value in records if kind == "follow up"]
    final = [value for kind, value in records if kind == "so the final answer is"]
    if final and not follow and len(records) == 1 and final[0]:
        return "answer", final[0]
    if len(follow) == 1 and not final and follow[0]:
        kinds = [kind for kind, _ in records]
        if kinds in (["follow up"], ["follow up", "intermediate answer"]):
            return "search", follow[0]
    raise ValueError("한 번의 검색 또는 최종 답만 출력해야 함")


def normalize_query(query):
    return " ".join(unicodedata.normalize("NFKC", query).casefold().split())


def run_self_ask(question, complete, search_answer, **options):
    """기존 호출 형식을 유지하되 실행은 LangGraph에 위임한다."""
    from self_ask_langgraph import build_self_ask_graph
    graph = build_self_ask_graph(complete, search_answer, **options)
    return graph.invoke({"question": question})
