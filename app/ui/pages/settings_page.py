"""Application appearance and scoring transparency."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, current_theme: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 26)
        layout.setSpacing(14)
        title = QLabel("Settings")
        title.setObjectName("title")
        subtitle = QLabel(
            "Customize appearance and review the decision model used across the portfolio."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        appearance = QFrame()
        appearance.setObjectName("card")
        appearance.setProperty("class", "card")
        form = QFormLayout(appearance)
        form.setContentsMargins(20, 20, 20, 20)
        self.theme = QComboBox()
        self.theme.addItems(["Light", "Dark"])
        self.theme.setCurrentText(current_theme.title())
        self.theme.currentTextChanged.connect(
            lambda value: self.theme_changed.emit(value.lower())
        )
        form.addRow("Appearance", self.theme)
        layout.addWidget(appearance)

        methodology = QFrame()
        methodology.setObjectName("card")
        methodology.setProperty("class", "card")
        box = QVBoxLayout(methodology)
        box.setContentsMargins(20, 18, 20, 20)
        heading = QLabel("Health Score Methodology")
        heading.setObjectName("section")
        details = QLabel(
            "Product Adoption 30%  •  Customer Engagement 20%  •  "
            "Support Health 20%  •  Customer Satisfaction 15%  •  Usage Trend 15%\n\n"
            "Categories: Healthy 85–100  ·  Stable 70–84  ·  "
            "At Risk 50–69  ·  Critical 0–49\n\n"
            "Risk is calculated independently from usage decline, support incidents, "
            "engagement gaps, renewal proximity, customer sentiment, and strategic "
            "revenue exposure."
        )
        details.setWordWrap(True)
        details.setObjectName("subtitle")
        box.addWidget(heading)
        box.addWidget(details)
        layout.addWidget(methodology)
        layout.addStretch()
