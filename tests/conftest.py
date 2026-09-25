"""Shared domain fixtures."""

import pytest

from app.database.models import Customer


@pytest.fixture
def healthy_customer() -> Customer:
    return Customer(
        id=1,
        company_name="Example Co",
        industry="Technology",
        account_owner="Maya Chen",
        customer_tier="Enterprise",
        annual_recurring_revenue=200_000,
        contract_start_date="2025-01-01",
        renewal_date="2026-12-01",
        monthly_active_users=90,
        licensed_users=100,
        usage_change_30d=10,
        open_support_tickets=0,
        critical_tickets=0,
        average_ticket_resolution_hours=3,
        customer_satisfaction_score=4.8,
        nps_score=70,
        last_meeting_date="2026-09-15",
        executive_sponsor="A Sponsor",
        primary_contact="A Contact",
        product_adoption_score=95,
        engagement_score=92,
        sentiment_score=94,
    )
