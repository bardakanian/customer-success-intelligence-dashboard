"""Portfolio-level metrics and calculated insights."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from app.database.models import Customer
from app.services.renewal_service import within_renewal_window
from app.services.risk_service import days_since_meeting
from app.utils.helpers import currency

HEALTH_CATEGORIES = ("Healthy", "Stable", "At Risk", "Critical")


def portfolio_metrics(
    customers: list[Customer],
    today: date | None = None,
) -> dict[str, float | int]:
    risky = [
        customer
        for customer in customers
        if customer.health_category in {"At Risk", "Critical"}
    ]
    renewals = [
        customer
        for customer in customers
        if within_renewal_window(customer, 90, today)
    ]
    return {
        "total": len(customers),
        "healthy": sum(
            customer.health_category == "Healthy" for customer in customers
        ),
        "at_risk": sum(
            customer.health_category == "At Risk" for customer in customers
        ),
        "critical": sum(
            customer.health_category == "Critical" for customer in customers
        ),
        "total_arr": sum(
            customer.annual_recurring_revenue for customer in customers
        ),
        "arr_at_risk": sum(
            customer.annual_recurring_revenue for customer in risky
        ),
        "renewal_arr_90": sum(
            customer.annual_recurring_revenue for customer in renewals
        ),
        "average_health": sum(
            customer.health_score for customer in customers
        )
        / max(len(customers), 1),
    }


def health_distribution(customers: list[Customer]) -> dict[str, int]:
    counts = Counter(customer.health_category for customer in customers)
    return {category: counts[category] for category in HEALTH_CATEGORIES}


def arr_by_health(customers: list[Customer]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for customer in customers:
        totals[customer.health_category] += customer.annual_recurring_revenue
    return {category: totals[category] for category in HEALTH_CATEGORIES}


def portfolio_insights(
    customers: list[Customer],
    today: date | None = None,
) -> list[str]:
    reference_date = today or date.today()
    high_risk = [
        customer
        for customer in customers
        if customer.risk_level in {"High", "Critical"}
    ]
    weak_renewals = [
        customer
        for customer in customers
        if within_renewal_window(customer, 90, reference_date)
        and customer.health_score < 70
    ]
    declines = [
        customer for customer in customers if customer.usage_change_30d < -20
    ]
    recent = [
        customer
        for customer in customers
        if days_since_meeting(customer, reference_date) <= 30
    ]
    average_recent_engagement = sum(
        customer.engagement_score for customer in recent
    ) / max(len(recent), 1)
    exposed_arr = sum(
        customer.annual_recurring_revenue for customer in high_risk
    )
    return [
        f"{currency(exposed_arr, compact=True)} ARR is associated with high or critical risk accounts.",
        f"{len(weak_renewals)} accounts renewing within 90 days have health scores below 70.",
        f"{len(declines)} customers have experienced usage declines greater than 20%.",
        f"Accounts with a meeting in the last 30 days average {average_recent_engagement:.0f}/100 engagement.",
    ]
