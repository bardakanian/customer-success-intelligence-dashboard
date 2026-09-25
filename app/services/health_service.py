"""Customer health score calculation."""

from __future__ import annotations

from app.database.models import Customer

HEALTHY_THRESHOLD = 85
STABLE_THRESHOLD = 70
AT_RISK_THRESHOLD = 50
HEALTH_THRESHOLDS = {
    "healthy": HEALTHY_THRESHOLD,
    "stable": STABLE_THRESHOLD,
    "at_risk": AT_RISK_THRESHOLD,
}

ADOPTION_WEIGHT = 0.30
ENGAGEMENT_WEIGHT = 0.20
SUPPORT_WEIGHT = 0.20
SATISFACTION_WEIGHT = 0.15
USAGE_TREND_WEIGHT = 0.15

CSAT_SHARE = 0.45
NPS_SHARE = 0.25
SENTIMENT_SHARE = 0.30


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def usage_trend_score(change_percent: float) -> float:
    """Normalize a usage change around a neutral score of 70."""
    return clamp(70 + change_percent * 1.5)


def support_health_score(
    open_tickets: int,
    critical_tickets: int,
    resolution_hours: float,
) -> float:
    ticket_penalty = min(open_tickets * 5, 30)
    critical_penalty = min(critical_tickets * 24, 48)
    resolution_penalty = max(0, min((resolution_hours - 4) * 1.5, 25))
    return round(
        clamp(100 - ticket_penalty - critical_penalty - resolution_penalty),
        1,
    )


def satisfaction_score(csat: float, nps: int, sentiment: float) -> float:
    csat_normalized = clamp(csat / 5 * 100)
    nps_normalized = clamp((nps + 100) / 2)
    return clamp(
        csat_normalized * CSAT_SHARE
        + nps_normalized * NPS_SHARE
        + sentiment * SENTIMENT_SHARE
    )


def calculate_health_score(customer: Customer) -> float:
    """Calculate health from adoption, engagement, support, satisfaction, and usage."""
    support = support_health_score(
        customer.open_support_tickets,
        customer.critical_tickets,
        customer.average_ticket_resolution_hours,
    )
    satisfaction = satisfaction_score(
        customer.customer_satisfaction_score,
        customer.nps_score,
        customer.sentiment_score,
    )
    score = (
        clamp(customer.product_adoption_score) * ADOPTION_WEIGHT
        + clamp(customer.engagement_score) * ENGAGEMENT_WEIGHT
        + support * SUPPORT_WEIGHT
        + satisfaction * SATISFACTION_WEIGHT
        + usage_trend_score(customer.usage_change_30d) * USAGE_TREND_WEIGHT
    )
    return round(clamp(score), 1)


def health_category(score: float) -> str:
    if score >= HEALTHY_THRESHOLD:
        return "Healthy"
    if score >= STABLE_THRESHOLD:
        return "Stable"
    if score >= AT_RISK_THRESHOLD:
        return "At Risk"
    return "Critical"


def enrich_health(customer: Customer) -> Customer:
    """Update a customer with the calculated health fields."""
    customer.support_score = support_health_score(
        customer.open_support_tickets,
        customer.critical_tickets,
        customer.average_ticket_resolution_hours,
    )
    customer.health_score = calculate_health_score(customer)
    customer.health_category = health_category(customer.health_score)
    return customer
