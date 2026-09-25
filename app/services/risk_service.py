"""Risk signals and overall account risk classification."""

from __future__ import annotations

from datetime import date, datetime

from app.database.models import Customer

HIGH_ARR_THRESHOLD = 150_000
LOW_ADOPTION_THRESHOLD = 55
LOW_ENGAGEMENT_THRESHOLD = 55
LOW_SATISFACTION_THRESHOLD = 3.5
SEVERE_USAGE_DECLINE = -35
USAGE_DECLINE = -20

CRITICAL_RISK_SCORE = 8
HIGH_RISK_SCORE = 5
MEDIUM_RISK_SCORE = 2

RISK_SIGNAL_WEIGHTS = {
    "Severe usage decline (>35%)": 3,
    "Critical support incident": 3,
    "Strategic ARR with declining health": 3,
    "Renewal within 30 days": 2,
    "Low satisfaction": 2,
    "Poor NPS": 2,
}


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_until_renewal(customer: Customer, today: date | None = None) -> int:
    return (parse_date(customer.renewal_date) - (today or date.today())).days


def days_since_meeting(customer: Customer, today: date | None = None) -> int:
    return ((today or date.today()) - parse_date(customer.last_meeting_date)).days


def risk_factors(customer: Customer, today: date | None = None) -> list[str]:
    """Return every material risk signal detected for an account."""
    factors: list[str] = []
    meeting_days = days_since_meeting(customer, today)
    renewal_days = days_until_renewal(customer, today)

    if customer.usage_change_30d < SEVERE_USAGE_DECLINE:
        factors.append("Severe usage decline (>35%)")
    elif customer.usage_change_30d < USAGE_DECLINE:
        factors.append("Usage decline (>20%)")

    if customer.critical_tickets:
        factors.append("Critical support incident")
    if customer.open_support_tickets >= 4:
        factors.append("Multiple unresolved tickets")

    if meeting_days > 60:
        factors.append("No customer meeting in 60+ days")
    elif meeting_days > 30:
        factors.append("No customer meeting in 30+ days")

    if 0 <= renewal_days <= 30:
        factors.append("Renewal within 30 days")
    elif 0 <= renewal_days <= 90:
        factors.append("Renewal within 90 days")

    if customer.product_adoption_score < LOW_ADOPTION_THRESHOLD:
        factors.append("Low product adoption")
    if customer.customer_satisfaction_score < LOW_SATISFACTION_THRESHOLD:
        factors.append("Low satisfaction")
    if customer.nps_score < 0:
        factors.append("Poor NPS")
    if customer.engagement_score < LOW_ENGAGEMENT_THRESHOLD:
        factors.append("Low engagement")
    if (
        customer.annual_recurring_revenue >= HIGH_ARR_THRESHOLD
        and customer.health_score < 65
    ):
        factors.append("Strategic ARR with declining health")
    return factors


def calculate_risk_level(customer: Customer, today: date | None = None) -> str:
    """Classify risk using independent signals plus the overall health score."""
    risk_score = sum(
        RISK_SIGNAL_WEIGHTS.get(factor, 1)
        for factor in risk_factors(customer, today)
    )
    if customer.health_score < 50:
        risk_score += 3
    elif customer.health_score < 70:
        risk_score += 1

    if risk_score >= CRITICAL_RISK_SCORE:
        return "Critical"
    if risk_score >= HIGH_RISK_SCORE:
        return "High"
    if risk_score >= MEDIUM_RISK_SCORE:
        return "Medium"
    return "Low"
