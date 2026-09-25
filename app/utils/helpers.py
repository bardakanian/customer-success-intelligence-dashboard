"""Display formatting helpers."""

from __future__ import annotations

from datetime import datetime


def currency(value: float, compact: bool = False) -> str:
    if compact and abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if compact and abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def display_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        return "—"
    return parsed.strftime("%b %d, %Y")
