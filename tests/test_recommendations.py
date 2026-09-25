from datetime import date

from app.services.health_service import enrich_health
from app.services.recommendation_service import recommendations

REFERENCE_DATE = date(2026, 9, 25)


def test_recommendations_reflect_customer_conditions(healthy_customer):
    healthy_customer.usage_change_30d = -30
    healthy_customer.critical_tickets = 1
    healthy_customer.open_support_tickets = 4
    healthy_customer.renewal_date = "2026-10-20"
    enrich_health(healthy_customer)

    actions = recommendations(healthy_customer, REFERENCE_DATE)

    assert any("support engineering" in action for action in actions)
    assert any("declining usage" in action for action in actions)


def test_recommendations_are_prioritized_and_limited(healthy_customer):
    healthy_customer.renewal_date = "2026-10-20"
    healthy_customer.health_score = 40
    healthy_customer.critical_tickets = 1
    healthy_customer.usage_change_30d = -40
    healthy_customer.product_adoption_score = 30
    healthy_customer.engagement_score = 30
    healthy_customer.customer_satisfaction_score = 2.5

    actions = recommendations(healthy_customer, REFERENCE_DATE)

    assert len(actions) == 4
    assert actions[0].startswith("Create a renewal recovery plan")


def test_healthy_account_gets_expansion_action(healthy_customer):
    enrich_health(healthy_customer)
    action = recommendations(healthy_customer, REFERENCE_DATE)[0]
    assert "expansion" in action
