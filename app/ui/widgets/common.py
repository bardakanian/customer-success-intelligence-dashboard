"""Reusable visual components shared by the dashboard pages."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

STATUS_COLORS = {
    "Healthy": "#168A68",
    "Stable": "#3478B8",
    "At Risk": "#C98119",
    "Critical": "#C94747",
    "Low": "#168A68",
    "Medium": "#3478B8",
    "High": "#C98119",
}


class MetricCard(QFrame):
    """Compact KPI card with an optional contextual caption."""

    def __init__(
        self,
        label: str,
        value: str,
        accent: str = "#2D6CDF",
        caption: str = "",
    ):
        super().__init__()
        self.setObjectName("card")
        self.setProperty("class", "card")
        self.setMinimumHeight(94)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 11)
        layout.setSpacing(3)

        label_widget = QLabel(label.upper())
        label_widget.setObjectName("metricLabel")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metric")
        caption_widget = QLabel(caption)
        caption_widget.setObjectName("subtitle")
        caption_widget.setWordWrap(True)
        accent_line = QFrame()
        accent_line.setFixedSize(28, 3)
        accent_line.setStyleSheet(
            f"background:{accent}; border:none; border-radius:1px;"
        )

        layout.addWidget(label_widget)
        layout.addWidget(self.value_label)
        layout.addWidget(caption_widget)
        layout.addWidget(accent_line)

        tooltips = {
            "annual recurring revenue": (
                "ARR is the account's annual recurring subscription revenue."
            ),
            "arr at risk": (
                "Recurring revenue associated with accounts below the healthy threshold."
            ),
        }
        if label.lower() in tooltips:
            self.setToolTip(tooltips[label.lower()])


class StatusBadge(QLabel):
    """Text badge that communicates status without relying only on color."""

    def __init__(self, status: str, prefix: str = ""):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(25)
        self.setContentsMargins(10, 2, 10, 2)
        self.set_status(status, prefix)

    def set_status(self, status: str, prefix: str = "") -> None:
        color = QColor(STATUS_COLORS.get(status, "#64748B"))
        self.setText(f"{prefix}{status}")
        self.setStyleSheet(
            f"background:rgba({color.red()},{color.green()},{color.blue()},32);"
            f"color:{color.name()};"
            f"border:1px solid rgba({color.red()},{color.green()},{color.blue()},78);"
            "border-radius:12px;font-size:11px;font-weight:700;padding:2px 8px;"
        )


class HealthScoreDisplay(QFrame):
    """Prominent score treatment for Customer 360."""

    def __init__(self, score: float, category: str):
        super().__init__()
        self.setObjectName("subtlePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(2)
        score_label = QLabel(f"{score:.0f} / 100")
        score_label.setObjectName("metric")
        score_label.setAlignment(Qt.AlignCenter)
        badge = StatusBadge(category)
        badge.setMaximumWidth(100)
        layout.addWidget(score_label)
        layout.addWidget(badge, 0, Qt.AlignCenter)
        self.setToolTip(
            "Health combines adoption, engagement, support, satisfaction, and usage trend."
        )


class EmptyStateTable(QTableWidget):
    """Table that explains when a query or filter returns no rows."""

    def __init__(self, rows: int, columns: int):
        super().__init__(rows, columns)
        self.empty_message = "No records to display."

    def set_empty_message(self, message: str) -> None:
        self.empty_message = message
        self.viewport().update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.rowCount() != 0:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        color = self.palette().color(self.foregroundRole())
        color.setAlpha(150)
        painter.setPen(color)
        font = painter.font()
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(
            self.viewport().rect().adjusted(20, 35, -20, -20),
            Qt.AlignCenter | Qt.TextWordWrap,
            self.empty_message,
        )


class BarChart(QWidget):
    """Small native Qt bar chart that follows the active palette."""

    def __init__(
        self,
        data: dict[str, float],
        colors: list[str] | None = None,
        money: bool = False,
    ):
        super().__init__()
        self.data = data
        self.money = money
        self.colors = colors or ["#2D6CDF"] * len(data)
        self.setMinimumHeight(145)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.data:
            return

        text_color = self.palette().color(self.foregroundRole())
        muted = QColor(text_color)
        muted.setAlpha(155)
        grid = QColor(text_color)
        grid.setAlpha(42)
        left, top, bottom = 24, 18, 30
        width = max(1, self.width() - left - 10)
        height = max(1, self.height() - top - bottom)
        max_value = max(self.data.values()) or 1
        slot = width / len(self.data)
        bar_width = min(44, slot * 0.48)

        painter.setPen(QPen(grid, 1))
        painter.drawLine(left, top + height, left + width, top + height)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        for index, (label, value) in enumerate(self.data.items()):
            bar_height = height * value / max_value
            x_position = left + slot * index + (slot - bar_width) / 2
            y_position = top + height - bar_height
            painter.setBrush(QColor(self.colors[index % len(self.colors)]))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                int(x_position),
                int(y_position),
                int(bar_width),
                int(bar_height),
                4,
                4,
            )
            painter.setPen(muted)
            painter.drawText(
                int(left + slot * index),
                int(top + height + 5),
                int(slot),
                22,
                Qt.AlignHCenter,
                label,
            )
            value_text = self._format_value(value)
            painter.drawText(
                int(left + slot * index),
                max(0, int(y_position - 19)),
                int(slot),
                17,
                Qt.AlignHCenter,
                value_text,
            )

    def _format_value(self, value: float) -> str:
        if not self.money:
            return f"{value:.0f}"
        if value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        return f"${value / 1_000:.0f}K"


def standard_table(
    headers: list[str],
    empty_message: str = "No records to display.",
) -> EmptyStateTable:
    table = EmptyStateTable(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.set_empty_message(empty_message)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setFocusPolicy(Qt.StrongFocus)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(44)
    table.horizontalHeader().setMinimumSectionSize(70)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    table.horizontalHeader().setStretchLastSection(True)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    return table


def configure_columns(
    table: QTableWidget,
    stretch: tuple[int, ...] = (),
    widths: dict[int, int] | None = None,
) -> None:
    header = table.horizontalHeader()
    for column in range(table.columnCount()):
        header.setSectionResizeMode(column, QHeaderView.Interactive)
    for column in stretch:
        header.setSectionResizeMode(column, QHeaderView.Stretch)
    for column, width in (widths or {}).items():
        table.setColumnWidth(column, width)


def card(title: str, child: QWidget, subtitle: str = "") -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    frame.setProperty("class", "card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(17, 14, 17, 16)
    layout.setSpacing(9)
    heading = QLabel(title)
    heading.setObjectName("section")
    layout.addWidget(heading)
    if subtitle:
        detail = QLabel(subtitle)
        detail.setObjectName("subtitle")
        detail.setWordWrap(True)
        layout.addWidget(detail)
    layout.addWidget(child)
    return frame


class SortItem(QTableWidgetItem):
    def __init__(self, text: str, key=None, numeric: bool = False):
        super().__init__(text)
        self.key = text if key is None else key
        if numeric:
            self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def __lt__(self, other) -> bool:
        other_key = other.key if isinstance(other, SortItem) else other.text()
        return self.key < other_key


class StatusItem(SortItem):
    def __init__(self, status: str, key=None):
        super().__init__(f"●  {status}", status if key is None else key)
        color_key = status.split("  |", 1)[0]
        self.setForeground(QColor(STATUS_COLORS.get(color_key, "#64748B")))
        font = self.font()
        font.setBold(True)
        self.setFont(font)
