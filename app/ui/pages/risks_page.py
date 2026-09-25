"""Focused risk command center."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.database.models import Customer
from app.services.recommendation_service import primary_recommendation
from app.services.risk_service import HIGH_ARR_THRESHOLD, days_until_renewal, risk_factors
from app.ui.widgets.common import (
    MetricCard,
    SortItem,
    StatusItem,
    configure_columns,
    standard_table,
)
from app.utils.helpers import currency, display_date

RISK_PRIORITY = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


class RisksPage(QWidget):
    account_selected = Signal(int)

    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 26)
        layout.setSpacing(14)
        title = QLabel("At-Risk Accounts")
        title.setObjectName("title")
        subtitle = QLabel(
            "Prioritize intervention using revenue exposure, renewal proximity, and risk drivers."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.metrics = QHBoxLayout()
        layout.addLayout(self.metrics)
        layout.addWidget(self._filter_toolbar())

        self.table = standard_table(
            [
                "Company",
                "ARR",
                "Health Score",
                "Risk Level",
                "Renewal Date",
                "Risk Drivers",
                "Recommended Action",
            ],
            "No at-risk accounts match these filters. Reset filters to view the full intervention queue.",
        )
        configure_columns(
            self.table,
            stretch=(0, 5, 6),
            widths={1: 105, 2: 100, 3: 105, 4: 120},
        )
        self.table.cellDoubleClicked.connect(self.open_row)
        layout.addWidget(self.table, 1)
        self.refresh()

    def _filter_toolbar(self) -> QFrame:
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        filters = QHBoxLayout(toolbar)
        filters.setContentsMargins(13, 9, 13, 9)
        filters.setSpacing(16)
        self.high_arr = QCheckBox("High ARR ($150K+)")
        self.renewal = QCheckBox("Renewal within 90 days")
        self.critical = QCheckBox("Critical incidents")
        self.decline = QCheckBox("Usage decline >20%")
        for check in (
            self.high_arr,
            self.renewal,
            self.critical,
            self.decline,
        ):
            check.toggled.connect(self.refresh)
            filters.addWidget(check)
        filters.addStretch()
        reset = QPushButton("Reset filters")
        reset.setObjectName("textButton")
        reset.clicked.connect(self.reset_filters)
        filters.addWidget(reset)
        return toolbar

    def reset_filters(self) -> None:
        for check in (
            self.high_arr,
            self.renewal,
            self.critical,
            self.decline,
        ):
            check.setChecked(False)
        self.refresh()

    @staticmethod
    def _clear_layout(layout) -> None:
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def refresh(self, *_args) -> None:
        at_risk = [
            customer
            for customer in self.database.customers()
            if customer.health_category in {"At Risk", "Critical"}
        ]
        self._clear_layout(self.metrics)
        at_risk_arr = sum(
            customer.annual_recurring_revenue for customer in at_risk
        )
        critical_count = sum(
            customer.risk_level == "Critical" for customer in at_risk
        )
        high_count = sum(customer.risk_level == "High" for customer in at_risk)
        upcoming_count = sum(
            0 <= days_until_renewal(customer) <= 90 for customer in at_risk
        )
        metric_cards = (
            ("ARR at Risk", currency(at_risk_arr, True), "#C94747", "Health below 70"),
            ("Critical Risk", str(critical_count), "#C94747", "Immediate intervention"),
            ("High Risk Accounts", str(high_count), "#C98119", "Active recovery plans"),
            ("At-Risk Renewals", str(upcoming_count), "#3478B8", "Due within 90 days"),
        )
        for values in metric_cards:
            self.metrics.addWidget(MetricCard(*values))

        filtered = [customer for customer in at_risk if self._matches(customer)]
        filtered.sort(
            key=lambda customer: (
                RISK_PRIORITY[customer.risk_level],
                days_until_renewal(customer),
                -customer.annual_recurring_revenue,
            )
        )
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered))
        for row, customer in enumerate(filtered):
            factors = risk_factors(customer)
            values = [
                QTableWidgetItem(customer.company_name),
                SortItem(currency(customer.annual_recurring_revenue), customer.annual_recurring_revenue, True),
                SortItem(f"{customer.health_score:.0f}", customer.health_score, True),
                StatusItem(customer.risk_level),
                SortItem(display_date(customer.renewal_date), customer.renewal_date),
                QTableWidgetItem(" • ".join(factors[:3])),
                QTableWidgetItem(primary_recommendation(customer)),
            ]
            values[0].setData(Qt.UserRole, customer.id)
            values[5].setToolTip(values[5].text())
            values[6].setToolTip(values[6].text())
            for column, item in enumerate(values):
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.table.sortItems(3, Qt.AscendingOrder)

    def _matches(self, customer: Customer) -> bool:
        if self.high_arr.isChecked() and (
            customer.annual_recurring_revenue < HIGH_ARR_THRESHOLD
        ):
            return False
        if self.renewal.isChecked() and not (
            0 <= days_until_renewal(customer) <= 90
        ):
            return False
        if self.critical.isChecked() and not customer.critical_tickets:
            return False
        if self.decline.isChecked() and customer.usage_change_30d >= -20:
            return False
        return True

    def open_row(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.account_selected.emit(item.data(Qt.UserRole))
