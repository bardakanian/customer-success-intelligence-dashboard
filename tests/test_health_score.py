from app.services.health_service import (
    calculate_health_score,
    health_category,
    support_health_score,
    usage_trend_score,
)


def test_healthy_inputs_produce_high_score(healthy_customer):
    assert calculate_health_score(healthy_customer) >= 85


def test_support_incidents_reduce_support_health():
    degraded = support_health_score(5, 1, 18)
    healthy = support_health_score(1, 0, 4)
    assert degraded < healthy


def test_usage_trend_is_clamped_to_score_range():
    assert usage_trend_score(100) == 100
    assert usage_trend_score(-100) == 0


def test_health_category_thresholds():
    assert health_category(85) == "Healthy"
    assert health_category(70) == "Stable"
    assert health_category(50) == "At Risk"
    assert health_category(49.9) == "Critical"
