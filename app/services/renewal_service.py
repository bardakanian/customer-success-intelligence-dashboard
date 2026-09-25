"""Renewal window calculations."""

from __future__ import annotations

from datetime import date

from app.database.models import Customer
from app.services.risk_service import days_until_renewal


def within_renewal_window(
    customer: Customer,
    days: int,
    today: date | None = None,
) -> bool:
    remaining = days_until_renewal(customer, today)
    return 0 <= remaining <= days


def renewal_metrics(
    customers: list[Customer],
    today: date | None = None,
) -> dict[str, float | int]:
    upcoming_30 = [
        customer
        for customer in customers
        if within_renewal_window(customer, 30, today)
    ]
    upcoming_90 = [
        customer
        for customer in customers
        if within_renewal_window(customer, 90, today)
    ]
    at_risk = [
        customer
        for customer in upcoming_90
        if customer.risk_level in {"High", "Critical"}
        or customer.health_score < 70
    ]
    return {
        "count_30": len(upcoming_30),
        "count_90": len(upcoming_90),
        "arr_90": sum(customer.annual_recurring_revenue for customer in upcoming_90),
        "arr_risk_90": sum(
            customer.annual_recurring_revenue for customer in at_risk
        ),
    }
