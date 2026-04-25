from healthbot.observability.metrics import MetricsRegistry


def test_metrics_registry_aggregates_timer_values():
    registry = MetricsRegistry()

    registry.observe("http.request.duration_ms", 10.0)
    registry.observe("http.request.duration_ms", 20.0)
    registry.observe("http.request.duration_ms", 30.0)

    snapshot = registry.snapshot()

    assert snapshot["timers"]["http.request.duration_ms"]["count"] == 3
    assert snapshot["timers"]["http.request.duration_ms"]["avg_ms"] == 20.0
    assert snapshot["timers"]["http.request.duration_ms"]["max_ms"] == 30.0
    assert snapshot["timers"]["http.request.duration_ms"]["total_ms"] == 60.0


def test_render_prometheus_includes_timer_aggregates():
    registry = MetricsRegistry()
    registry.observe("span.health_agent.duration_ms", 15.0)
    registry.observe("span.health_agent.duration_ms", 25.0)

    output = registry.render_prometheus()

    assert "span_health_agent_duration_ms_count 2" in output
    assert "span_health_agent_duration_ms_sum 40.0" in output
    assert "span_health_agent_duration_ms_avg 20.0" in output
    assert "span_health_agent_duration_ms_max 25.0" in output
