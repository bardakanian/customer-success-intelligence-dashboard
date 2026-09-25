from dataclasses import replace
from datetime import date

from app.services.analytics_service import (
    arr_by_health,
    health_distribution,
    portfolio_metrics,
)


def test_portfolio_metrics_calculate_arr_exposure(healthy_customer):
    healthy_customer.health_score = 92
    healthy_customer.health_category = "Healthy"
    healthy_customer.renewal_date = "2027-05-01"
    risky_customer = replace(
        healthy_customer,
        id=2,
        company_name="Risk Example",
        annual_recurring_revenue=125_000,
        renewal_date="2026-10-20",
        health_score=55,
        health_category="At Risk",
        risk_level="High",
    )

    metrics = portfolio_metrics(
        [healthy_customer, risky_customer],
        today=date(2026, 9, 25),
    )

    assert metrics["total"] == 2
    assert metrics["healthy"] == 1
    assert metrics["at_risk"] == 1
    assert metrics["total_arr"] == 325_000
    assert metrics["arr_at_risk"] == 125_000
    assert metrics["renewal_arr_90"] == 125_000


def test_health_breakdowns_include_zero_value_categories(healthy_customer):
    healthy_customer.health_category = "Healthy"

    assert health_distribution([healthy_customer]) == {
        "Healthy": 1,
        "Stable": 0,
        "At Risk": 0,
        "Critical": 0,
    }
    assert arr_by_health([healthy_customer])["Healthy"] == 200_000
    assert arr_by_health([healthy_customer])["Critical"] == 0
