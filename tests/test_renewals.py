from datetime import date

from app.services.renewal_service import renewal_metrics, within_renewal_window

REFERENCE_DATE = date(2026, 9, 25)


def test_renewal_windows_include_the_boundary(healthy_customer):
    healthy_customer.renewal_date = "2026-10-25"
    assert within_renewal_window(healthy_customer, 30, REFERENCE_DATE)
    assert not within_renewal_window(healthy_customer, 29, REFERENCE_DATE)


def test_past_renewals_are_excluded(healthy_customer):
    healthy_customer.renewal_date = "2026-09-24"
    assert not within_renewal_window(healthy_customer, 90, REFERENCE_DATE)


def test_renewal_metrics_sum_at_risk_arr(healthy_customer):
    healthy_customer.renewal_date = "2026-10-20"
    healthy_customer.risk_level = "High"

    metrics = renewal_metrics([healthy_customer], REFERENCE_DATE)

    assert metrics["count_30"] == 1
    assert metrics["arr_90"] == 200_000
    assert metrics["arr_risk_90"] == 200_000
