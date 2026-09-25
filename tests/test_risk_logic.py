from datetime import date

from app.services.health_service import enrich_health
from app.services.risk_service import calculate_risk_level, risk_factors

REFERENCE_DATE = date(2026, 9, 25)


def test_healthy_account_has_low_risk(healthy_customer):
    enrich_health(healthy_customer)
    assert calculate_risk_level(healthy_customer, REFERENCE_DATE) == "Low"


def test_risk_combines_operational_and_commercial_signals(healthy_customer):
    healthy_customer.usage_change_30d = -42
    healthy_customer.critical_tickets = 1
    healthy_customer.open_support_tickets = 6
    healthy_customer.product_adoption_score = 40
    healthy_customer.engagement_score = 35
    healthy_customer.last_meeting_date = "2026-06-01"
    healthy_customer.renewal_date = "2026-10-10"
    enrich_health(healthy_customer)

    factors = risk_factors(healthy_customer, REFERENCE_DATE)

    assert "Critical support incident" in factors
    assert "Renewal within 30 days" in factors
    assert "Low product adoption" in factors
    assert calculate_risk_level(healthy_customer, REFERENCE_DATE) == "Critical"


def test_risk_is_not_determined_only_by_health(healthy_customer):
    enrich_health(healthy_customer)
    healthy_customer.critical_tickets = 1

    assert healthy_customer.health_score >= 85
    assert calculate_risk_level(healthy_customer, REFERENCE_DATE) == "Medium"
