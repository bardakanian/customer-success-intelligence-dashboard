"""Main application shell and navigation."""

from __future__ import annotations

from PySide6.QtCore import QDateTime, QSettings, Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.ui.pages.account_detail_page import AccountDetailPage
from app.ui.pages.accounts_page import AccountsPage
from app.ui.pages.activities_page import ActivitiesPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.renewals_page import RenewalsPage
from app.ui.pages.risks_page import RisksPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.styles import DARK, LIGHT

PAGE_TITLES = [
    "Dashboard",
    "Accounts",
    "At-Risk Accounts",
    "Renewals",
    "Activities",
    "Settings",
]


class MainWindow(QMainWindow):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        self.setWindowTitle("Customer Success Intelligence Dashboard")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 700)

        self.settings = QSettings(
            "Portfolio Labs", "Customer Success Intelligence"
        )
        self.theme = self.settings.value("theme", "light")

        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        shell.addWidget(self._sidebar())

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._header())
        shell.addWidget(content, 1)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        self.dashboard = DashboardPage(database)
        self.accounts = AccountsPage(database)
        self.risks = RisksPage(database)
        self.renewals = RenewalsPage(database)
        self.activities = ActivitiesPage(database)
        self.detail = AccountDetailPage(database)
        self.settings_page = SettingsPage(self.theme)
        self.pages = [
            self.dashboard,
            self.accounts,
            self.risks,
            self.renewals,
            self.activities,
            self.settings_page,
        ]
        for page in self.pages:
            self.stack.addWidget(page)
        self.stack.addWidget(self.detail)

        for page in (
            self.dashboard,
            self.accounts,
            self.risks,
            self.renewals,
        ):
            page.account_selected.connect(self.open_account)
        self.detail.back_requested.connect(lambda: self.navigate(1))
        self.detail.feedback.connect(self.show_feedback)
        self.settings_page.theme_changed.connect(self.apply_theme)

        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage(
            f"Local portfolio  •  {len(database.customers())} accounts  •  SQLite connected"
        )
        self.apply_theme(self.theme)
        self.navigate(0)

    def _sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(224)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 21, 14, 16)
        layout.setSpacing(6)

        brand = QLabel("  ◈  CS INTELLIGENCE")
        brand.setStyleSheet(
            "font-size:14px;font-weight:800;letter-spacing:1px;"
        )
        tagline = QLabel("     Portfolio command center")
        tagline.setStyleSheet("color:#7F91AA;font-size:10px;")
        layout.addWidget(brand)
        layout.addWidget(tagline)
        layout.addSpacing(19)

        workspace_label = QLabel("WORKSPACE")
        workspace_label.setObjectName("navSection")
        layout.addWidget(workspace_label)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons: list[QPushButton] = []
        entries = [
            ("▦   Dashboard", 0),
            ("◎   Accounts", 1),
            ("△   At-Risk Accounts", 2),
            ("↻   Renewals", 3),
            ("≡   Activities", 4),
        ]
        for text, index in entries:
            button = self._nav_button(text)
            button.clicked.connect(
                lambda checked=False, page_index=index: self.navigate(page_index)
            )
            self.nav_group.addButton(button)
            self.nav_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()
        preferences_label = QLabel("PREFERENCES")
        preferences_label.setObjectName("navSection")
        layout.addWidget(preferences_label)

        settings_button = self._nav_button("⚙   Settings")
        settings_button.clicked.connect(lambda: self.navigate(5))
        self.nav_group.addButton(settings_button)
        self.nav_buttons.append(settings_button)
        layout.addWidget(settings_button)

        version = QLabel("  DEMO WORKSPACE  •  v1.0")
        version.setStyleSheet("color:#607089;font-size:9px;")
        layout.addWidget(version)
        return sidebar

    @staticmethod
    def _nav_button(text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("nav")
        button.setCheckable(True)
        button.setMinimumHeight(41)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 22, 0)
        layout.setSpacing(12)

        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("headerTitle")
        layout.addWidget(self.header_title)

        status = QLabel("●  Data current")
        status.setStyleSheet(
            "color:#168A68;font-size:11px;font-weight:700;"
        )
        status.setToolTip(
            "Customer metrics were loaded successfully from the local database."
        )
        layout.addWidget(status)
        layout.addStretch()

        search = QLineEdit()
        search.setPlaceholderText("Search accounts…")
        search.setClearButtonEnabled(True)
        search.setFixedWidth(250)
        search.setToolTip("Search by company, industry, or account owner")
        search.returnPressed.connect(lambda: self._global_search(search.text()))
        layout.addWidget(search)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("secondary")
        self.theme_button.setToolTip(
            "Switch between light and dark appearance"
        )
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        today = QLabel(QDateTime.currentDateTime().toString("MMM d, yyyy"))
        today.setObjectName("subtitle")
        layout.addWidget(today)
        return header

    def _global_search(self, text: str) -> None:
        self.navigate(1)
        self.accounts.search.setText(text)
        self.accounts.search.setFocus()

    def navigate(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.nav_buttons[index].setChecked(True)
        self.header_title.setText(PAGE_TITLES[index])
        page = self.pages[index]
        if hasattr(page, "refresh"):
            page.refresh()

    def open_account(self, customer_id: int) -> None:
        self.detail.load_customer(customer_id)
        self.stack.setCurrentWidget(self.detail)
        self.header_title.setText("Customer 360")
        for button in self.nav_buttons:
            button.setChecked(False)

    def apply_theme(self, theme: str) -> None:
        self.theme = theme
        self.settings.setValue("theme", theme)
        stylesheet = DARK if theme == "dark" else LIGHT
        QApplication.instance().setStyleSheet(stylesheet)
        self.theme_button.setText("☀  Light" if theme == "dark" else "☾  Dark")

        self.settings_page.theme.blockSignals(True)
        self.settings_page.theme.setCurrentText(theme.title())
        self.settings_page.theme.blockSignals(False)

    def toggle_theme(self) -> None:
        self.apply_theme("light" if self.theme == "dark" else "dark")
        self.show_feedback(f"{self.theme.title()} theme enabled")

    def show_feedback(self, message: str) -> None:
        self.statusBar().showMessage(message, 4000)
