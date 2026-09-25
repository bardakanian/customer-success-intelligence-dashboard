"""Portfolio-wide customer activity history."""

from __future__ import annotations

from PySide6.QtCore import Qt
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
from app.ui.widgets.common import SortItem, configure_columns, standard_table
from app.utils.helpers import display_date

ACTIVITY_TYPES = [
    "Customer Meeting",
    "Support Escalation",
    "Executive Business Review",
    "Email",
    "Renewal Discussion",
    "Product Training",
    "Internal Note",
    "Incident Review",
]


class ActivitiesPage(QWidget):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 26)
        layout.setSpacing(14)

        title = QLabel("Activity Log")
        title.setObjectName("title")
        subtitle = QLabel(
            "A portfolio-wide record of meetings, communications, training, and customer events."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self._filter_toolbar())

        self.table = standard_table(
            ["Date", "Company", "Activity Type", "Title", "Owner", "Description"],
            "No activities match your search or selected activity type.",
        )
        configure_columns(
            self.table,
            stretch=(1, 3, 5),
            widths={0: 115, 2: 165, 4: 120},
        )
        layout.addWidget(self.table, 1)
        self.search.textChanged.connect(self.refresh)
        self.kind.currentTextChanged.connect(self.refresh)
        self.refresh()

    def _filter_toolbar(self) -> QFrame:
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        filters = QHBoxLayout(toolbar)
        filters.setContentsMargins(12, 9, 12, 9)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search company, owner, title, or description…"
        )
        self.search.setClearButtonEnabled(True)
        self.kind = QComboBox()
        self.kind.addItems(["All activity types", *ACTIVITY_TYPES])
        self.result_count = QLabel()
        self.result_count.setObjectName("subtitle")
        reset = QPushButton("Reset filters")
        reset.setObjectName("textButton")
        reset.clicked.connect(self.reset_filters)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.kind, 1)
        filters.addWidget(self.result_count)
        filters.addWidget(reset)
        return toolbar

    def reset_filters(self) -> None:
        self.search.clear()
        self.kind.setCurrentIndex(0)
        self.refresh()

    def refresh(self, *_args) -> None:
        query = self.search.text().lower().strip()
        selected_type = self.kind.currentText()
        activities = []
        for activity in self.database.activities():
            searchable = (
                f'{activity["company_name"]} {activity["owner"]} '
                f'{activity["description"]} {activity["title"]}'
            ).lower()
            if query and query not in searchable:
                continue
            if (
                selected_type != "All activity types"
                and activity["activity_type"] != selected_type
            ):
                continue
            activities.append(activity)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(activities))
        self.result_count.setText(f"{len(activities)} activities")
        for row, activity in enumerate(activities):
            values = [
                SortItem(
                    display_date(activity["activity_date"]),
                    activity["activity_date"],
                ),
                QTableWidgetItem(activity["company_name"]),
                QTableWidgetItem(activity["activity_type"]),
                QTableWidgetItem(activity["title"]),
                QTableWidgetItem(activity["owner"]),
                QTableWidgetItem(activity["description"]),
            ]
            for column, item in enumerate(values):
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.DescendingOrder)
