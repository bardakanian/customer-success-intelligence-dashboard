"""Deterministic next-best-action rules."""

from __future__ import annotations

from datetime import date

from app.database.models import Customer
from app.services.risk_service import days_until_renewal


def recommendations(customer: Customer, today: date | None = None) -> list[str]:
    """Return up to four actions ordered by customer-success urgency."""
    actions: list[str] = []
    renewal_days = days_until_renewal(customer, today)

    if 0 <= renewal_days <= 90 and customer.health_score < 70:
        actions.append(
            "Create a renewal recovery plan and schedule an executive account review."
        )
    if customer.critical_tickets:
        actions.append(
            "Coordinate with support engineering and provide an incident update within 24 hours."
        )
    if customer.usage_change_30d < -20:
        actions.append("Schedule an adoption review and investigate declining usage.")
    if customer.product_adoption_score < 55:
        actions.append(
            "Review unused capabilities and schedule targeted product enablement."
        )
    if customer.engagement_score < 55:
        actions.append(
            "Schedule a customer check-in and confirm current business priorities."
        )
    if customer.customer_satisfaction_score < 3.5 or customer.nps_score < 0:
        actions.append(
            "Close the feedback loop with a documented service-improvement plan."
        )
    if not actions:
        actions.append(
            "Continue regular engagement and identify expansion opportunities."
        )
    return actions[:4]


def primary_recommendation(customer: Customer, today: date | None = None) -> str:
    return recommendations(customer, today)[0]
