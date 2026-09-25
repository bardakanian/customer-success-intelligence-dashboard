"""Searchable and filterable account portfolio."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.database.models import Customer
from app.services.risk_service import days_until_renewal
from app.ui.widgets.common import (
    SortItem,
    StatusItem,
    configure_columns,
    standard_table,
)
from app.utils.helpers import currency, display_date

RENEWAL_WINDOWS = {
    "Next 30 days": 30,
    "Next 90 days": 90,
    "Next 180 days": 180,
}


class AccountsPage(QWidget):
    account_selected = Signal(int)

    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 26)
        layout.setSpacing(14)

        title = QLabel("Accounts")
        title.setObjectName("title")
        subtitle = QLabel(
            "Monitor customer health, adoption, support activity, and renewal risk."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self._filter_toolbar())

        self.table = standard_table(
            [
                "Company",
                "Industry",
                "Tier",
                "ARR",
                "Health",
                "Score",
                "Usage Trend",
                "Open Tickets",
                "Renewal Date",
                "Risk Level",
            ],
            "No accounts match the selected filters. Try resetting or broadening your search.",
        )
        configure_columns(
            self.table,
            stretch=(0, 1),
            widths={2: 90, 3: 95, 4: 105, 5: 72, 6: 100, 7: 90, 8: 120, 9: 100},
        )
        self.table.cellDoubleClicked.connect(self.open_row)
        layout.addWidget(self.table, 1)

        industries = sorted({customer.industry for customer in database.customers()})
        self.industry.addItems(["All industries", *industries])
        for widget in (
            self.search,
            self.health,
            self.risk,
            self.tier,
            self.industry,
            self.renewal,
        ):
            signal = (
                widget.textChanged
                if widget is self.search
                else widget.currentTextChanged
            )
            signal.connect(self.refresh)
        self.refresh()

    def _filter_toolbar(self) -> QFrame:
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QVBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(8)

        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search company, industry, or account owner…"
        )
        self.search.setClearButtonEnabled(True)
        self.result_count = QLabel()
        self.result_count.setObjectName("subtitle")
        reset = QPushButton("Reset filters")
        reset.setObjectName("textButton")
        reset.clicked.connect(self.reset_filters)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(self.result_count)
        search_row.addWidget(reset)
        toolbar_layout.addLayout(search_row)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        self.health = QComboBox()
        self.health.addItems(["All health", "Healthy", "Stable", "At Risk", "Critical"])
        self.risk = QComboBox()
        self.risk.addItems(["All risk", "Low", "Medium", "High", "Critical"])
        self.tier = QComboBox()
        self.tier.addItems(["All tiers", "Enterprise", "Growth", "Standard"])
        self.industry = QComboBox()
        self.renewal = QComboBox()
        self.renewal.addItems(["Any renewal", *RENEWAL_WINDOWS])
        for widget in (
            self.health,
            self.risk,
            self.tier,
            self.industry,
            self.renewal,
        ):
            filters.addWidget(widget, 1)
        toolbar_layout.addLayout(filters)
        return toolbar

    def reset_filters(self) -> None:
        self.search.clear()
        for combo in (
            self.health,
            self.risk,
            self.tier,
            self.industry,
            self.renewal,
        ):
            combo.setCurrentIndex(0)
        self.refresh()

    def refresh(self, *_args) -> None:
        query = self.search.text().lower().strip()
        customers = self.database.customers()
        renewal_window = RENEWAL_WINDOWS.get(self.renewal.currentText())
        filtered = [
            customer
            for customer in customers
            if self._matches(customer, query, renewal_window)
        ]

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered))
        self.result_count.setText(f"{len(filtered)} of {len(customers)} accounts")
        for row, customer in enumerate(filtered):
            values = [
                QTableWidgetItem(customer.company_name),
                QTableWidgetItem(customer.industry),
                QTableWidgetItem(customer.customer_tier),
                SortItem(
                    currency(customer.annual_recurring_revenue),
                    customer.annual_recurring_revenue,
                    True,
                ),
                StatusItem(customer.health_category),
                SortItem(f"{customer.health_score:.0f}", customer.health_score, True),
                SortItem(
                    f"{customer.usage_change_30d:+.0f}%",
                    customer.usage_change_30d,
                    True,
                ),
                SortItem(
                    str(customer.open_support_tickets),
                    customer.open_support_tickets,
                    True,
                ),
                SortItem(display_date(customer.renewal_date), customer.renewal_date),
                StatusItem(customer.risk_level),
            ]
            values[0].setData(Qt.UserRole, customer.id)
            usage_color = "#168A68" if customer.usage_change_30d >= 0 else "#C94747"
            values[6].setForeground(QColor(usage_color))
            for column, item in enumerate(values):
                self.table.setItem(row, column, item)

        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.AscendingOrder)

    def _matches(
        self,
        customer: Customer,
        query: str,
        renewal_window: int | None,
    ) -> bool:
        searchable = (
            f"{customer.company_name} {customer.industry} {customer.account_owner}"
        ).lower()
        if query and query not in searchable:
            return False
        if self.health.currentText() != "All health" and (
            customer.health_category != self.health.currentText()
        ):
            return False
        if self.risk.currentText() != "All risk" and (
            customer.risk_level != self.risk.currentText()
        ):
            return False
        if self.tier.currentText() != "All tiers" and (
            customer.customer_tier != self.tier.currentText()
        ):
            return False
        if self.industry.currentText() != "All industries" and (
            customer.industry != self.industry.currentText()
        ):
            return False
        if renewal_window is not None and not (
            0 <= days_until_renewal(customer) <= renewal_window
        ):
            return False
        return True

    def open_row(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.account_selected.emit(item.data(Qt.UserRole))
