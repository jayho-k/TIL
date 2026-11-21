"""에이전트를 한 번 더 거칠 때 시간이 얼마나 늘어나는지 잰다."""
import statistics
import time

import httpx

import orchestrator

def timed_call(base: str, text: str) -> tuple[float, dict]:
    """앞에서 만든 call로 부르고, 걸린 시간을 함께 돌려준다."""
    start = time.perf_counter()
    data = orchestrator.call({"name": base, "_base": base}, text)
    return time.perf_counter() - start, data

def compare(targets: dict[str, str], text: str, rounds: int = 3) -> None:
    """대상을 번갈아 부르며 잰다."""
    times = {who: [] for who in targets}
    for i in range(rounds):
        for who, base in targets.items():
            seconds, data = timed_call(base, text)
            times[who].append(seconds)
            print(f"  {i + 1}회차 {who:8} {seconds:5.1f}초  source={data.get('source', '-')}")
    print()
    for who, ts in times.items():
        print(f"  {who:8} 중앙값 {statistics.median(ts):5.1f}초 · 최소 {min(ts):5.1f} · 최대 {max(ts):5.1f}")

def round_trip(targets: dict[str, str], rounds: int = 20) -> None:
    """모델을 쓰지 않는 요청으로 HTTP 왕복 한 번에 드는 시간만 잰다."""
    for who, base in targets.items():
        ts = []
        for _ in range(rounds):
            start = time.perf_counter()
            httpx.get(f"{base}/.well-known/agent-card.json", timeout=10).raise_for_status()
            ts.append((time.perf_counter() - start) * 1000)
        print(f"  {who:8} 중앙값 {statistics.median(ts):5.1f}ms · 최대 {max(ts):5.1f}ms")