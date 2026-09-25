"""Executive portfolio overview."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.services.analytics_service import (
    arr_by_health,
    health_distribution,
    portfolio_insights,
    portfolio_metrics,
)
from app.services.recommendation_service import primary_recommendation
from app.services.risk_service import risk_factors
from app.ui.widgets.common import (
    BarChart,
    MetricCard,
    SortItem,
    StatusItem,
    card,
    configure_columns,
    standard_table,
)
from app.utils.helpers import currency, display_date

RISK_PRIORITY = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
HEALTH_COLORS = ["#1F9D76", "#3B82C4", "#E59B2F", "#D55252"]


class DashboardPage(QWidget):
    account_selected = Signal(int)

    def __init__(self, database: Database):
        super().__init__()
        self.database = database

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        self.content_layout = QVBoxLayout(body)
        self.content_layout.setContentsMargins(26, 22, 26, 26)
        self.content_layout.setSpacing(16)

        title = QLabel("Portfolio Overview")
        title.setObjectName("title")
        subtitle = QLabel(
            "Health, revenue exposure, and the customer signals that need action today."
        )
        subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(title)
        self.content_layout.addWidget(subtitle)

        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(12)
        for column in range(4):
            self.metrics_grid.setColumnStretch(column, 1)
        self.content_layout.addLayout(self.metrics_grid)

        analytics = QHBoxLayout()
        analytics.setSpacing(12)
        self.health_chart_host = QVBoxLayout()
        self.arr_chart_host = QVBoxLayout()
        self.insights_layout = QVBoxLayout()
        self.insights_layout.setSpacing(7)
        analytics.addWidget(
            self._chart_shell("Health Distribution", self.health_chart_host), 1
        )
        analytics.addWidget(
            self._chart_shell("ARR by Health", self.arr_chart_host), 1
        )
        analytics.addWidget(
            card(
                "Portfolio Insights",
                self._insights_widget(),
                "Calculated from current account signals.",
            ),
            1,
        )
        self.content_layout.addLayout(analytics)

        self.table = standard_table(
            [
                "Company",
                "Health",
                "ARR",
                "Renewal",
                "Tickets",
                "Primary Risk",
                "Recommended Action",
            ],
            "No priority accounts require attention.",
        )
        self.table.setMinimumHeight(285)
        self.table.cellDoubleClicked.connect(self._open_row)
        configure_columns(
            self.table,
            stretch=(0, 5, 6),
            widths={1: 135, 2: 100, 3: 120, 4: 78},
        )
        self.content_layout.addWidget(
            card(
                "Accounts Requiring Attention",
                self.table,
                "Sorted by risk urgency. Double-click an account to open Customer 360.",
            )
        )
        self.refresh()

    @staticmethod
    def _chart_shell(title: str, content_layout: QVBoxLayout) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setProperty("class", "card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(7)
        label = QLabel(title)
        label.setObjectName("section")
        layout.addWidget(label)
        layout.addLayout(content_layout)
        return frame

    def _insights_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background:transparent;")
        widget.setLayout(self.insights_layout)
        return widget

    @staticmethod
    def _clear_layout(layout) -> None:
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def refresh(self) -> None:
        customers = self.database.customers()
        metrics = portfolio_metrics(customers)

        self._clear_layout(self.metrics_grid)
        metric_cards = [
            ("Total Customers", str(metrics["total"]), "#2D6CDF", "Active portfolio"),
            ("Healthy Accounts", str(metrics["healthy"]), "#1F9D76", "85+ health score"),
            ("At-Risk Accounts", str(metrics["at_risk"]), "#E59B2F", "Needs intervention"),
            ("Critical Accounts", str(metrics["critical"]), "#D55252", "Immediate action"),
            ("Total ARR", currency(metrics["total_arr"], True), "#6457C5", "Managed revenue"),
            ("ARR at Risk", currency(metrics["arr_at_risk"], True), "#D55252", "At Risk + Critical"),
            ("90-Day Renewals", currency(metrics["renewal_arr_90"], True), "#2D6CDF", "Renewing ARR"),
            ("Average Health", f'{metrics["average_health"]:.0f}', "#1F9D76", "Portfolio score"),
        ]
        for index, values in enumerate(metric_cards):
            self.metrics_grid.addWidget(
                MetricCard(*values), index // 4, index % 4
            )

        self._clear_layout(self.health_chart_host)
        self._clear_layout(self.arr_chart_host)
        self.health_chart_host.addWidget(
            BarChart(health_distribution(customers), HEALTH_COLORS)
        )
        self.arr_chart_host.addWidget(
            BarChart(arr_by_health(customers), HEALTH_COLORS, money=True)
        )

        self._clear_layout(self.insights_layout)
        for insight in portfolio_insights(customers):
            label = QLabel(f"•  {insight}")
            label.setWordWrap(True)
            label.setObjectName("subtitle")
            self.insights_layout.addWidget(label)
        self.insights_layout.addStretch()

        urgent = sorted(
            customers,
            key=lambda customer: (
                RISK_PRIORITY[customer.risk_level],
                customer.health_score,
            ),
        )[:8]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(urgent))
        for row, customer in enumerate(urgent):
            factors = risk_factors(customer)
            values = [
                QTableWidgetItem(customer.company_name),
                StatusItem(
                    f"{customer.health_category}  |  {customer.health_score:.0f}",
                    customer.health_score,
                ),
                SortItem(
                    currency(customer.annual_recurring_revenue),
                    customer.annual_recurring_revenue,
                    True,
                ),
                SortItem(display_date(customer.renewal_date), customer.renewal_date),
                SortItem(
                    str(customer.open_support_tickets),
                    customer.open_support_tickets,
                    True,
                ),
                QTableWidgetItem(factors[0] if factors else "Monitor"),
                QTableWidgetItem(primary_recommendation(customer)),
            ]
            values[0].setData(Qt.UserRole, customer.id)
            values[5].setToolTip(values[5].text())
            values[6].setToolTip(values[6].text())
            for column, item in enumerate(values):
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.table.sortItems(1, Qt.AscendingOrder)

    def _open_row(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.account_selected.emit(item.data(Qt.UserRole))
