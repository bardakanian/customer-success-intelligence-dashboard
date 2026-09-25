"""Lightweight domain models used across database, services, and UI."""
from __future__ import annotations
from dataclasses import dataclass, fields
from typing import Any, Mapping

@dataclass(slots=True)
class Customer:
    id: int | None
    company_name: str
    industry: str
    account_owner: str
    customer_tier: str
    annual_recurring_revenue: float
    contract_start_date: str
    renewal_date: str
    monthly_active_users: int
    licensed_users: int
    usage_change_30d: float
    open_support_tickets: int
    critical_tickets: int
    average_ticket_resolution_hours: float
    customer_satisfaction_score: float
    nps_score: int
    last_meeting_date: str
    executive_sponsor: str
    primary_contact: str
    product_adoption_score: float
    engagement_score: float
    sentiment_score: float
    health_score: float = 0
    health_category: str = "Critical"
    support_score: float = 0
    risk_level: str = "Low"

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Customer":
        field_names = {field.name for field in fields(cls)}
        return cls(
            **{key: row[key] for key in field_names if key in row.keys()}
        )
