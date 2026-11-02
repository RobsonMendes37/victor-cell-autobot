"""
SRE & Enterprise Observabilidade Service.
Collects runtime metrics, latency statistics, intent breakdowns, and exposes Prometheus-compatible metrics.
"""

import time
from typing import Any, Dict, List


class MetricsCollector:
    """
    In-memory Prometheus-compatible metrics aggregator.
    Tracks throughput, latencies, circuit breaker transitions, and conversation outcomes.
    """

    def __init__(self) -> None:
        self.start_time: float = time.time()
        self.messages_received_total: int = 0
        self.messages_processed_total: int = 0
        self.messages_ai_replied_total: int = 0
        self.messages_fallback_replied_total: int = 0
        self.handoffs_total: int = 0
        self.orders_created_total: int = 0
        self.rate_limited_total: int = 0
        self.errors_total: int = 0
        self._latencies: List[float] = []
        self._max_latencies_stored: int = 1000

    def record_received(self) -> None:
        self.messages_received_total += 1

    def record_processed(self, duration_seconds: float, replied_by_ai: bool = True) -> None:
        self.messages_processed_total += 1
        if replied_by_ai:
            self.messages_ai_replied_total += 1
        else:
            self.messages_fallback_replied_total += 1

        self._latencies.append(duration_seconds)
        if len(self._latencies) > self._max_latencies_stored:
            self._latencies.pop(0)

    def record_handoff(self) -> None:
        self.handoffs_total += 1

    def record_order_created(self) -> None:
        self.orders_created_total += 1

    def record_rate_limit(self) -> None:
        self.rate_limited_total += 1

    def record_error(self) -> None:
        self.errors_total += 1

    def get_latency_stats(self) -> Dict[str, float]:
        if not self._latencies:
            return {"avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0}

        sorted_lat = sorted(self._latencies)
        count = len(sorted_lat)
        avg = sum(sorted_lat) / count
        p50 = sorted_lat[int(count * 0.50)]
        p95 = sorted_lat[min(int(count * 0.95), count - 1)]
        max_lat = sorted_lat[-1]

        return {
            "avg_ms": round(avg * 1000, 2),
            "p50_ms": round(p50 * 1000, 2),
            "p95_ms": round(p95 * 1000, 2),
            "max_ms": round(max_lat * 1000, 2),
        }

    def get_summary_dict(self) -> Dict[str, Any]:
        uptime_seconds = int(time.time() - self.start_time)
        lat = self.get_latency_stats()
        fallback_rate = 0.0
        if self.messages_processed_total > 0:
            fallback_rate = round(
                (self.messages_fallback_replied_total / self.messages_processed_total) * 100, 2
            )

        return {
            "uptime_seconds": uptime_seconds,
            "messages_received_total": self.messages_received_total,
            "messages_processed_total": self.messages_processed_total,
            "messages_ai_replied_total": self.messages_ai_replied_total,
            "messages_fallback_replied_total": self.messages_fallback_replied_total,
            "fallback_rate_percentage": fallback_rate,
            "handoffs_total": self.handoffs_total,
            "orders_created_total": self.orders_created_total,
            "rate_limited_total": self.rate_limited_total,
            "errors_total": self.errors_total,
            "latency": lat,
        }

    def to_prometheus_format(self, circuit_state_code: int = 0) -> str:
        """
        Generates standard Prometheus text exposition format (version 0.0.4).
        circuit_state_code: 0=CLOSED (healthy), 1=HALF_OPEN, 2=OPEN (failing).
        """
        lines = [
            "# HELP pecasbot_uptime_seconds Total seconds since application startup",
            "# TYPE pecasbot_uptime_seconds gauge",
            f"pecasbot_uptime_seconds {int(time.time() - self.start_time)}",
            "",
            "# HELP pecasbot_messages_received_total Total incoming messages received",
            "# TYPE pecasbot_messages_received_total counter",
            f"pecasbot_messages_received_total {self.messages_received_total}",
            "",
            "# HELP pecasbot_messages_processed_total Total messages processed by pipeline",
            "# TYPE pecasbot_messages_processed_total counter",
            f"pecasbot_messages_processed_total {self.messages_processed_total}",
            "",
            "# HELP pecasbot_messages_ai_replied_total Messages successfully answered by Gemini LLM",
            "# TYPE pecasbot_messages_ai_replied_total counter",
            f"pecasbot_messages_ai_replied_total {self.messages_ai_replied_total}",
            "",
            "# HELP pecasbot_messages_fallback_replied_total Messages resolved by deterministic fallback",
            "# TYPE pecasbot_messages_fallback_replied_total counter",
            f"pecasbot_messages_fallback_replied_total {self.messages_fallback_replied_total}",
            "",
            "# HELP pecasbot_handoffs_total Total customer conversations escalated to human staff",
            "# TYPE pecasbot_handoffs_total counter",
            f"pecasbot_handoffs_total {self.handoffs_total}",
            "",
            "# HELP pecasbot_orders_created_total Total reservation orders successfully generated",
            "# TYPE pecasbot_orders_created_total counter",
            f"pecasbot_orders_created_total {self.orders_created_total}",
            "",
            "# HELP pecasbot_rate_limited_total Requests blocked by rate limiting",
            "# TYPE pecasbot_rate_limited_total counter",
            f"pecasbot_rate_limited_total {self.rate_limited_total}",
            "",
            "# HELP pecasbot_errors_total Total unhandled pipeline exceptions",
            "# TYPE pecasbot_errors_total counter",
            f"pecasbot_errors_total {self.errors_total}",
            "",
            "# HELP pecasbot_circuit_breaker_state State of the AI circuit breaker (0=CLOSED, 1=HALF_OPEN, 2=OPEN)",
            "# TYPE pecasbot_circuit_breaker_state gauge",
            f"pecasbot_circuit_breaker_state {circuit_state_code}",
            "",
        ]
        lat = self.get_latency_stats()
        lines.extend(
            [
                "# HELP pecasbot_processing_latency_p95_ms 95th percentile latency in milliseconds",
                "# TYPE pecasbot_processing_latency_p95_ms gauge",
                f"pecasbot_processing_latency_p95_ms {lat['p95_ms']}",
                "",
                "# HELP pecasbot_processing_latency_avg_ms Average processing latency in milliseconds",
                "# TYPE pecasbot_processing_latency_avg_ms gauge",
                f"pecasbot_processing_latency_avg_ms {lat['avg_ms']}",
            ]
        )
        return "\n".join(lines) + "\n"


# Singleton global de métricas
metrics_collector = MetricsCollector()
