"""Renewal pipeline and revenue exposure."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.services.recommendation_service import primary_recommendation
from app.services.renewal_service import renewal_metrics
from app.services.risk_service import days_until_renewal
from app.ui.widgets.common import (
    MetricCard,
    SortItem,
    StatusItem,
    configure_columns,
    standard_table,
)
from app.utils.helpers import currency, display_date


class RenewalsPage(QWidget):
    account_selected = Signal(int)

    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 26)
        layout.setSpacing(14)

        title = QLabel("Renewals")
        title.setObjectName("title")
        subtitle = QLabel(
            "Track upcoming contract events and intervene early where customer health creates exposure."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.metrics = QHBoxLayout()
        layout.addLayout(self.metrics)
        layout.addWidget(self._window_selector())

        self.table = standard_table(
            [
                "Company",
                "ARR",
                "Renewal Date",
                "Days Remaining",
                "Health",
                "Risk Level",
                "Recommended Action",
            ],
            "No renewals fall within this window.",
        )
        configure_columns(
            self.table,
            stretch=(0, 6),
            widths={1: 110, 2: 125, 3: 135, 4: 150, 5: 105},
        )
        self.table.cellDoubleClicked.connect(self.open_row)
        layout.addWidget(self.table, 1)
        self.refresh()

    def _window_selector(self) -> QFrame:
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        row = QHBoxLayout(toolbar)
        row.setContentsMargins(13, 8, 13, 8)
        row.addWidget(QLabel("Renewal window"))
        self.window_group = QButtonGroup(self)
        self.window_group.setExclusive(True)
        self.window_buttons: list[QPushButton] = []
        for days in (30, 60, 90, 180):
            button = QPushButton(f"{days} days")
            button.setObjectName("segment")
            button.setCheckable(True)
            button.setProperty("days", days)
            button.clicked.connect(self.refresh)
            self.window_group.addButton(button)
            self.window_buttons.append(button)
            row.addWidget(button)
        self.window_buttons[2].setChecked(True)
        row.addStretch()
        return toolbar

    def selected_days(self) -> int:
        button = self.window_group.checkedButton()
        return int(button.property("days")) if button else 90

    @staticmethod
    def _clear_layout(layout) -> None:
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def refresh(self, *_args) -> None:
        customers = self.database.customers()
        metrics = renewal_metrics(customers)
        self._clear_layout(self.metrics)
        metric_cards = (
            ("Next 30 Days", str(metrics["count_30"]), "#2D6CDF", "Renewal events"),
            ("Next 90 Days", str(metrics["count_90"]), "#6457C5", "Renewal events"),
            ("ARR Next 90", currency(metrics["arr_90"], True), "#1F9D76", "Renewing revenue"),
            ("At-Risk Renewal ARR", currency(metrics["arr_risk_90"], True), "#D55252", "High attention"),
        )
        for values in metric_cards:
            self.metrics.addWidget(MetricCard(*values))

        window = self.selected_days()
        renewals = [
            customer
            for customer in customers
            if 0 <= days_until_renewal(customer) <= window
        ]
        renewals.sort(
            key=lambda customer: (
                days_until_renewal(customer),
                customer.health_score,
            )
        )

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(renewals))
        for row, customer in enumerate(renewals):
            remaining = days_until_renewal(customer)
            remaining_label = (
                f"Due soon  •  {remaining}" if remaining <= 30 else str(remaining)
            )
            values = [
                QTableWidgetItem(customer.company_name),
                SortItem(currency(customer.annual_recurring_revenue), customer.annual_recurring_revenue, True),
                SortItem(display_date(customer.renewal_date), customer.renewal_date),
                SortItem(remaining_label, remaining, True),
                StatusItem(f"{customer.health_category}  |  {customer.health_score:.0f}", customer.health_score),
                StatusItem(customer.risk_level),
                QTableWidgetItem(primary_recommendation(customer)),
            ]
            values[0].setData(Qt.UserRole, customer.id)
            values[6].setToolTip(values[6].text())
            for column, item in enumerate(values):
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.table.sortItems(3, Qt.AscendingOrder)

    def open_row(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.account_selected.emit(item.data(Qt.UserRole))
