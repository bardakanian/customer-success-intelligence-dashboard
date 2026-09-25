"""Deterministic, correlated fictional portfolio data."""

from __future__ import annotations

from datetime import date, timedelta
from typing import NamedTuple

from app.database.models import Customer
from app.services.health_service import enrich_health
from app.services.risk_service import calculate_risk_level

COMPANIES = [
    ("Northstar Logistics", "Logistics"),
    ("Vertex Analytics", "Technology"),
    ("Summit Financial", "Financial Services"),
    ("BluePeak Health", "Healthcare"),
    ("Horizon Retail Group", "Retail"),
    ("Atlas Manufacturing", "Manufacturing"),
    ("Nova Systems", "Technology"),
    ("BrightPath Education", "Education"),
    ("Redwood Commerce", "E-commerce"),
    ("Cobalt Security", "Cybersecurity"),
    ("Evergreen Energy", "Energy"),
    ("HarborPoint Insurance", "Insurance"),
    ("Apex BioSciences", "Life Sciences"),
    ("Silverline Media", "Media"),
    ("Ironwood Construction", "Construction"),
    ("Clearwater Telecom", "Telecommunications"),
    ("Keystone Legal", "Professional Services"),
    ("Orbit Mobility", "Transportation"),
    ("Luminary Labs", "Technology"),
    ("Crescent Hospitality", "Hospitality"),
    ("Pioneer Foods", "Food & Beverage"),
    ("Meridian Aviation", "Aerospace"),
    ("TrueNorth Public Sector", "Government"),
    ("Ember Creative", "Media"),
    ("Granite Industrial", "Manufacturing"),
    ("Willow Wellness", "Healthcare"),
    ("Quantum Workforce", "Human Resources"),
    ("Beacon Property Group", "Real Estate"),
    ("Solstice Networks", "Technology"),
    ("Oak & River Markets", "Retail"),
]

OWNERS = ["Maya Chen", "Jordan Brooks", "Priya Shah", "Alex Morgan", "Sam Rivera"]
SPONSORS = [
    "Elena Rodriguez, COO",
    "Marcus Lee, CIO",
    "Avery Thompson, VP Operations",
    "Noah Williams, CTO",
    "Amara Patel, CDO",
]
CONTACTS = [
    "Taylor Kim",
    "Jamie Parker",
    "Riley Davis",
    "Morgan Bell",
    "Casey Nguyen",
    "Drew Foster",
]

RENEWAL_OFFSETS = [
    18, 44, 72, 110, 156, 205, 265, 330, 28, 83,
    134, 175, 238, 294, 352, 56, 96, 145, 190, 247,
    315, 21, 66, 121, 181, 221, 279, 340, 38, 88,
]
ARR_BASE_BY_TIER = {"Enterprise": 210_000, "Growth": 105_000, "Standard": 48_000}


class AccountProfile(NamedTuple):
    adoption: int
    engagement: int
    usage_change: int
    open_tickets: int
    critical_tickets: int
    resolution_hours: float
    csat: float
    nps: int
    sentiment: int


# These profiles keep related signals coherent instead of randomizing each field.
PROFILES = [
    AccountProfile(94, 91, 12, 1, 0, 3.1, 4.8, 72, 94),
    AccountProfile(86, 82, 5, 2, 0, 5.0, 4.4, 49, 86),
    AccountProfile(75, 78, -3, 2, 0, 6.5, 4.1, 31, 78),
    AccountProfile(63, 61, -14, 3, 0, 9.0, 3.8, 18, 66),
    AccountProfile(48, 43, -28, 5, 1, 16.0, 3.0, -18, 42),
    AccountProfile(35, 31, -42, 7, 2, 25.0, 2.6, -42, 28),
    AccountProfile(91, 74, 8, 5, 1, 12.0, 3.9, 22, 68),
    AccountProfile(57, 47, -22, 1, 0, 5.5, 3.5, 3, 56),
]


def customer_tier(index: int) -> str:
    tier_position = index % 5
    if tier_position in {0, 1}:
        return "Enterprise"
    if tier_position in {2, 3}:
        return "Growth"
    return "Standard"


def build_customers(today: date | None = None) -> list[Customer]:
    reference_date = today or date.today()
    customers: list[Customer] = []

    for index, (company, industry) in enumerate(COMPANIES):
        profile = PROFILES[index % len(PROFILES)]
        variance = (index % 3) - 1
        tier = customer_tier(index)
        annual_revenue = ARR_BASE_BY_TIER[tier] + (index * 17_000) % 135_000
        licensed_users = 180 + (index * 73) % 920
        adoption = profile.adoption + variance * 2
        active_users = int(
            licensed_users * max(0.25, min(0.96, adoption / 100))
        )
        meeting_days = max(3, 105 - profile.engagement + index % 14)

        customer = Customer(
            id=None,
            company_name=company,
            industry=industry,
            account_owner=OWNERS[index % len(OWNERS)],
            customer_tier=tier,
            annual_recurring_revenue=annual_revenue,
            contract_start_date=(
                reference_date - timedelta(days=365 + index * 7)
            ).isoformat(),
            renewal_date=(
                reference_date + timedelta(days=RENEWAL_OFFSETS[index])
            ).isoformat(),
            monthly_active_users=active_users,
            licensed_users=licensed_users,
            usage_change_30d=profile.usage_change + variance * 2,
            open_support_tickets=max(0, profile.open_tickets + variance),
            critical_tickets=profile.critical_tickets,
            average_ticket_resolution_hours=max(
                2, profile.resolution_hours + variance
            ),
            customer_satisfaction_score=max(
                1, min(5, profile.csat + variance * 0.1)
            ),
            nps_score=profile.nps + variance * 3,
            last_meeting_date=(
                reference_date - timedelta(days=meeting_days)
            ).isoformat(),
            executive_sponsor=SPONSORS[index % len(SPONSORS)],
            primary_contact=CONTACTS[index % len(CONTACTS)],
            product_adoption_score=max(0, adoption),
            engagement_score=max(0, profile.engagement + variance * 2),
            sentiment_score=max(0, profile.sentiment + variance * 2),
        )
        enrich_health(customer)
        customer.risk_level = calculate_risk_level(customer, reference_date)
        customers.append(customer)
    return customers


def activity_history(
    customer_id: int,
    owner: str,
    today: date | None = None,
) -> list[tuple]:
    reference_date = today or date.today()
    activity_types = [
        "Customer Meeting",
        "Email",
        "Product Training",
        "Executive Business Review",
    ]
    titles = [
        "Success plan review",
        "Follow-up on adoption goals",
        "Workflow enablement session",
        "Quarterly outcomes review",
    ]
    return [
        (
            customer_id,
            (reference_date - timedelta(days=days)).isoformat(),
            activity_types[index],
            titles[index],
            "Reviewed objectives, open actions, and customer outcomes.",
            owner,
        )
        for index, days in enumerate((12, 31, 58, 91))
    ]
