from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class Metrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.active_sse_connections = Gauge(
            "active_sse_connections",
            "Currently open SSE responses",
            ("transport",),
            registry=self.registry,
        )
        self.active_agent_runs = Gauge(
            "active_agent_runs",
            "Currently executing Agent runs",
            registry=self.registry,
        )
        self.stream_events = Counter(
            "stream_events_total",
            "Application SSE events",
            ("transport", "event"),
            registry=self.registry,
        )
        self.stream_duration = Histogram(
            "stream_duration_seconds",
            "End-to-end stream duration",
            ("transport", "status"),
            registry=self.registry,
        )
