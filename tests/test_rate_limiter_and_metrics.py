"""
Test Suite for SlidingWindowRateLimiter and MetricsCollector.
Validates DoS protection, quota tracking, latency calculation, and Prometheus export.
"""

import time

from fastapi.testclient import TestClient

from infrastructure.services.metrics_service import MetricsCollector
from infrastructure.services.rate_limiter import SlidingWindowRateLimiter
from presentation.api import app


def test_rate_limiter_allows_up_to_limit():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10.0)
    key = "5585988887777"

    # 1ª requisição
    allowed, info = limiter.is_allowed(key)
    assert allowed is True
    assert info["remaining"] == 2

    # 2ª requisição
    allowed, info = limiter.is_allowed(key)
    assert allowed is True
    assert info["remaining"] == 1

    # 3ª requisição
    allowed, info = limiter.is_allowed(key)
    assert allowed is True
    assert info["remaining"] == 0

    # 4ª requisição: bloqueada por estourar o limite
    allowed, info = limiter.is_allowed(key)
    assert allowed is False
    assert info["remaining"] == 0
    assert info["retry_after"] > 0


def test_rate_limiter_slides_and_cleans_up():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.1)
    key = "5585999991111"

    limiter.is_allowed(key)
    limiter.is_allowed(key)
    allowed, _ = limiter.is_allowed(key)
    assert allowed is False

    # Espera a janela expirar
    time.sleep(0.12)
    allowed, info = limiter.is_allowed(key)
    assert allowed is True
    assert info["remaining"] == 1

    # Testa limpeza de chaves expiradas
    cleaned = limiter.cleanup()
    assert cleaned >= 0


def test_metrics_collector_calculations_and_prometheus_export():
    collector = MetricsCollector()
    collector.record_received()
    collector.record_processed(duration_seconds=0.05, replied_by_ai=True)
    collector.record_processed(duration_seconds=0.15, replied_by_ai=False)
    collector.record_handoff()
    collector.record_order_created()
    collector.record_rate_limit()

    summary = collector.get_summary_dict()
    assert summary["messages_received_total"] == 1
    assert summary["messages_processed_total"] == 2
    assert summary["messages_ai_replied_total"] == 1
    assert summary["messages_fallback_replied_total"] == 1
    assert summary["fallback_rate_percentage"] == 50.0
    assert summary["handoffs_total"] == 1
    assert summary["orders_created_total"] == 1
    assert summary["rate_limited_total"] == 1

    prom_text = collector.to_prometheus_format(circuit_state_code=0)
    assert "pecasbot_messages_received_total 1" in prom_text
    assert "pecasbot_messages_processed_total 2" in prom_text
    assert "pecasbot_handoffs_total 1" in prom_text
    assert "pecasbot_circuit_breaker_state 0" in prom_text


def test_api_metrics_endpoint_and_health_integration():
    client = TestClient(app)

    # 1. Endpoint /health contém informações do circuit breaker e métricas
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "circuit_breaker" in data
    assert "metrics" in data

    # 2. Endpoint /metrics padrão Prometheus
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "text/plain" in res_metrics.headers["content-type"]
    assert "pecasbot_uptime_seconds" in res_metrics.text
