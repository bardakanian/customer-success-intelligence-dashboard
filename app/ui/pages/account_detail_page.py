"""Customer 360 account workspace with persistent notes and activities."""
from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.database.database import Database
from app.database.models import Customer
from app.services.recommendation_service import recommendations
from app.services.risk_service import days_since_meeting, days_until_renewal, risk_factors
from app.ui.dialogs import EntryDialog
from app.ui.widgets.common import HealthScoreDisplay, MetricCard, StatusBadge
from app.utils.helpers import currency, display_date


class AccountDetailPage(QWidget):
    back_requested = Signal()
    feedback = Signal(str)

    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        self.customer_id = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        self.body = QWidget()
        scroll.setWidget(self.body)
        self.layout_ = QVBoxLayout(self.body)
        self.layout_.setContentsMargins(26, 18, 26, 28)
        self.layout_.setSpacing(14)

    def load_customer(self, customer_id: int) -> None:
        self.customer_id = customer_id
        self.refresh()

    def _clear(self) -> None:
        while self.layout_.count():
            item = self.layout_.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def refresh(self) -> None:
        self._clear()
        customer = self.database.customer(self.customer_id)
        if not customer:
            empty = QLabel("This account could not be loaded. Return to Accounts and try again.")
            empty.setObjectName("subtitle")
            self.layout_.addWidget(empty)
            return
        top = QHBoxLayout()
        back = QPushButton("←  Back to accounts")
        back.setObjectName("textButton")
        back.clicked.connect(self.back_requested)
        top.addWidget(back)
        top.addStretch()
        self.layout_.addLayout(top)
        self.layout_.addWidget(self._account_header(customer))
        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        metric_data = (
            (
                "Annual Recurring Revenue",
                currency(customer.annual_recurring_revenue),
                "#6457C5",
                customer.customer_tier,
            ),
            (
                "Renewal",
                display_date(customer.renewal_date),
                "#3478B8",
                f"{days_until_renewal(customer)} days remaining",
            ),
            (
                "Open Support Tickets",
                str(customer.open_support_tickets),
                "#C98119",
                f"{customer.critical_tickets} critical",
            ),
            (
                "Last Customer Meeting",
                f"{days_since_meeting(customer)} days ago",
                "#168A68",
                f"Engagement {customer.engagement_score:.0f}/100",
            ),
        )
        for data in metric_data:
            metrics.addWidget(MetricCard(*data), 1)
        self.layout_.addLayout(metrics)
        columns = QHBoxLayout()
        columns.setSpacing(12)
        columns.addWidget(self._signals_card(customer), 1)
        columns.addWidget(self._risk_action_card(customer), 1)
        self.layout_.addLayout(columns)
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        activity_count = len(self.database.activities(customer.id))
        note_count = len(self.database.notes(customer.id))
        tabs.addTab(
            self._activities_tab(customer),
            f"Activity Timeline  ({activity_count})",
        )
        tabs.addTab(self._notes_tab(customer), f"Notes  ({note_count})")
        self.layout_.addWidget(tabs)

    def _account_header(self, customer: Customer) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setProperty("class", "card")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 17, 20, 17)
        layout.setSpacing(14)
        identity = QVBoxLayout()
        identity.setSpacing(5)
        eyebrow = QLabel("CUSTOMER 360")
        eyebrow.setObjectName("eyebrow")
        name = QLabel(customer.company_name)
        name.setObjectName("title")
        context = QLabel(
            f"{customer.industry}  •  {customer.customer_tier}  •  "
            f"Account owner: {customer.account_owner}"
        )
        context.setObjectName("subtitle")
        contacts = QLabel(
            f"Executive sponsor: {customer.executive_sponsor}   •   "
            f"Primary contact: {customer.primary_contact}"
        )
        contacts.setObjectName("subtitle")
        contacts.setWordWrap(True)
        identity.addWidget(eyebrow)
        identity.addWidget(name)
        identity.addWidget(context)
        identity.addWidget(contacts)
        layout.addLayout(identity, 1)
        layout.addWidget(HealthScoreDisplay(customer.health_score, customer.health_category))
        risk_box = QVBoxLayout()
        risk_title = QLabel("OVERALL RISK")
        risk_title.setObjectName("eyebrow")
        risk_title.setAlignment(Qt.AlignCenter)
        risk_box.addWidget(risk_title)
        risk_box.addWidget(StatusBadge(customer.risk_level, "Risk: "))
        risk_box.addStretch()
        layout.addLayout(risk_box)
        return frame

    def _signals_card(self, customer: Customer) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setProperty("class", "card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(17, 14, 17, 16)
        layout.setSpacing(8)
        title = QLabel("Customer Signals")
        title.setObjectName("section")
        subtitle = QLabel("Current product, support, engagement, and sentiment indicators.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        signals = [
            (
                "Product adoption",
                customer.product_adoption_score,
                f"{customer.monthly_active_users:,} of "
                f"{customer.licensed_users:,} licensed users",
            ),
            (
                "Engagement",
                customer.engagement_score,
                f"Last meeting {days_since_meeting(customer)} days ago",
            ),
            (
                "Support health",
                customer.support_score,
                f"{customer.open_support_tickets} open • "
                f"{customer.critical_tickets} critical • "
                f"{customer.average_ticket_resolution_hours:.1f}h avg resolution",
            ),
            (
                "Customer sentiment",
                customer.sentiment_score,
                f"CSAT {customer.customer_satisfaction_score:.1f}/5 • "
                f"NPS {customer.nps_score:+d}",
            ),
        ]
        for label, value, caption in signals:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addStretch()
            score = QLabel(f"{value:.0f} / 100")
            score.setStyleSheet("font-weight:700;")
            row.addWidget(score)
            layout.addLayout(row)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(value))
            bar.setTextVisible(False)
            bar.setFixedHeight(7)
            layout.addWidget(bar)
            detail = QLabel(caption)
            detail.setObjectName("subtitle")
            layout.addWidget(detail)
        usage = QLabel(f"30-day usage change   {customer.usage_change_30d:+.1f}%")
        usage_color = "#168A68" if customer.usage_change_30d >= 0 else "#C94747"
        usage.setStyleSheet(
            f"font-weight:700;color:{usage_color};padding-top:4px;"
        )
        layout.addWidget(usage)
        return frame

    def _risk_action_card(self, customer: Customer) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setProperty("class", "card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(17, 14, 17, 16)
        layout.setSpacing(7)
        title = QLabel("Risk Drivers")
        title.setObjectName("section")
        layout.addWidget(title)
        factors = risk_factors(customer)
        if not factors:
            clean = QLabel("✓  No material risk signals detected")
            clean.setStyleSheet("color:#168A68; font-weight:700; padding:7px 0;")
            layout.addWidget(clean)
        for factor in factors:
            layout.addWidget(self._risk_row(factor, customer))
        action_title = QLabel("Recommended Actions")
        action_title.setObjectName("section")
        layout.addSpacing(5)
        layout.addWidget(action_title)
        for index, action in enumerate(recommendations(customer), 1):
            layout.addWidget(self._action_row(index, action, customer))
        layout.addStretch()
        return frame

    def _risk_row(self, factor: str, customer: Customer) -> QFrame:
        row = QFrame()
        row.setObjectName("subtlePanel")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setSpacing(9)
        critical_terms = ("Severe", "Critical", "within 30", "Strategic")
        severity = "Critical" if any(term in factor for term in critical_terms) else "High"
        badge = StatusBadge(severity)
        badge.setFixedWidth(67)
        text = QVBoxLayout()
        text.setSpacing(1)
        heading = QLabel(factor)
        heading.setStyleSheet("font-weight:700;")
        detail = QLabel(self._risk_explanation(factor, customer))
        detail.setObjectName("subtitle")
        detail.setWordWrap(True)
        text.addWidget(heading)
        text.addWidget(detail)
        layout.addWidget(badge, 0, Qt.AlignTop)
        layout.addLayout(text, 1)
        return row

    @staticmethod
    def _risk_explanation(factor: str, customer: Customer) -> str:
        if "usage decline" in factor.lower():
            return (
                f"Usage changed {customer.usage_change_30d:+.1f}% during the last 30 days."
            )
        if "Critical support" in factor:
            return (
                f"{customer.critical_tickets} critical ticket(s) require coordinated resolution."
            )
        if "unresolved" in factor:
            return f"{customer.open_support_tickets} support tickets remain open."
        if "meeting" in factor:
            return (
                f"The last customer meeting was {days_since_meeting(customer)} days ago."
            )
        if "Renewal" in factor:
            return f"Contract renewal is {days_until_renewal(customer)} days away."
        if "adoption" in factor:
            return f"Product adoption is {customer.product_adoption_score:.0f}/100."
        if "satisfaction" in factor:
            return (
                f"Customer satisfaction is {customer.customer_satisfaction_score:.1f}/5."
            )
        if "NPS" in factor:
            return f"The current NPS response is {customer.nps_score:+d}."
        if "engagement" in factor:
            return f"Engagement is {customer.engagement_score:.0f}/100."
        if "Strategic ARR" in factor:
            return (
                f"{currency(customer.annual_recurring_revenue)} ARR is exposed "
                "while health is below 65."
            )
        return "This signal contributes to the account's overall risk classification."

    def _action_row(self, index: int, action: str, customer: Customer) -> QFrame:
        row = QFrame()
        row.setObjectName("subtlePanel")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 7, 10, 7)
        number = QLabel(str(index))
        number.setAlignment(Qt.AlignCenter)
        number.setFixedSize(23, 23)
        number.setStyleSheet("background:#2D6CDF;color:white;border-radius:11px;font-size:11px;font-weight:700;")
        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        text = QLabel(action)
        text.setWordWrap(True)
        text.setStyleSheet("font-weight:600;")
        reason = QLabel(self._action_reason(action, customer))
        reason.setObjectName("subtitle")
        reason.setWordWrap(True)
        text_box.addWidget(text)
        text_box.addWidget(reason)
        layout.addWidget(number, 0, Qt.AlignTop)
        layout.addLayout(text_box, 1)
        return row

    @staticmethod
    def _action_reason(action: str, customer: Customer) -> str:
        lowered = action.lower()
        if "renewal recovery" in lowered:
            return (
                f"Health is {customer.health_score:.0f}/100 with renewal in "
                f"{days_until_renewal(customer)} days."
            )
        if "support engineering" in lowered:
            return (
                f"The account has {customer.critical_tickets} critical and "
                f"{customer.open_support_tickets} total open tickets."
            )
        if "declining usage" in lowered:
            return (
                f"Usage changed {customer.usage_change_30d:+.1f}% in the last 30 days."
            )
        if "enablement" in lowered:
            return (
                f"Product adoption is currently {customer.product_adoption_score:.0f}/100."
            )
        if "check-in" in lowered:
            return (
                f"Engagement is {customer.engagement_score:.0f}/100; last meeting "
                f"was {days_since_meeting(customer)} days ago."
            )
        if "feedback loop" in lowered:
            return (
                f"CSAT is {customer.customer_satisfaction_score:.1f}/5 and "
                f"NPS is {customer.nps_score:+d}."
            )
        return f"The account is {customer.health_category.lower()} with {customer.risk_level.lower()} overall risk."

    def _activities_tab(self, customer):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 12, 10, 12)
        controls = QHBoxLayout()
        description = QLabel("Customer touchpoints and internal account events")
        description.setObjectName("subtitle")
        controls.addWidget(description)
        controls.addStretch()
        button = QPushButton("+  Add activity")
        button.setObjectName("primary")
        button.clicked.connect(lambda: self._add("Activity", customer))
        controls.addWidget(button)
        layout.addLayout(controls)
        rows = self.database.activities(customer.id)
        if not rows:
            empty = QLabel("No activity has been recorded for this account yet.")
            empty.setObjectName("subtitle")
            empty.setAlignment(Qt.AlignCenter)
            empty.setMinimumHeight(100)
            layout.addWidget(empty)
        for activity in rows:
            layout.addWidget(self._activity_entry(activity))
        layout.addStretch()
        return widget

    def _activity_entry(self, activity):
        frame = QFrame()
        frame.setObjectName("subtlePanel")
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 9, 12, 9)
        row.setSpacing(12)
        date = QLabel(display_date(activity["activity_date"]))
        date.setObjectName("metricLabel")
        date.setFixedWidth(95)
        content = QVBoxLayout()
        content.setSpacing(2)
        top = QHBoxLayout()
        title = QLabel(activity["title"])
        title.setStyleSheet("font-weight:700;")
        activity_type = QLabel(activity["activity_type"])
        activity_type.setStyleSheet("color:#3478B8;font-size:11px;font-weight:700;")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(activity_type)
        description = QLabel(activity["description"])
        description.setObjectName("subtitle")
        description.setWordWrap(True)
        owner = QLabel(f"Owner: {activity['owner']}")
        owner.setObjectName("eyebrow")
        content.addLayout(top)
        content.addWidget(description)
        content.addWidget(owner)
        row.addWidget(date, 0, Qt.AlignTop)
        row.addLayout(content, 1)
        return frame

    def _notes_tab(self, customer):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 12, 10, 12)
        controls = QHBoxLayout()
        description = QLabel("Shared context and decisions for the account team")
        description.setObjectName("subtitle")
        controls.addWidget(description)
        controls.addStretch()
        button = QPushButton("+  Add note")
        button.setObjectName("primary")
        button.clicked.connect(lambda: self._add("Note", customer))
        controls.addWidget(button)
        layout.addLayout(controls)
        notes = self.database.notes(customer.id)
        if not notes:
            empty = QLabel("No notes yet. Add the first account note to share context with the team.")
            empty.setObjectName("subtitle")
            empty.setAlignment(Qt.AlignCenter)
            empty.setMinimumHeight(100)
            layout.addWidget(empty)
        for note in notes:
            box = QFrame()
            box.setObjectName("subtlePanel")
            line = QVBoxLayout(box)
            line.setContentsMargins(13, 10, 13, 10)
            line.setSpacing(5)
            meta = QLabel(f'{note["author"]}  •  {display_date(note["note_date"])}')
            meta.setObjectName("metricLabel")
            text = QLabel(note["note_text"])
            text.setWordWrap(True)
            line.addWidget(meta)
            line.addWidget(text)
            layout.addWidget(box)
        layout.addStretch()
        return widget

    def _add(self, mode, customer):
        dialog = EntryDialog(mode, customer.account_owner, self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            if mode == "Activity":
                self.database.add_activity(
                    customer.id,
                    dialog.kind.currentText(),
                    dialog.title.text(),
                    dialog.text.toPlainText(),
                    dialog.owner.text(),
                )
            else:
                self.database.add_note(customer.id, dialog.owner.text(), dialog.text.toPlainText())
            self.refresh()
            self.feedback.emit("Activity saved." if mode == "Activity" else "Note added.")
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Unable to save", f"The {mode.lower()} could not be saved. {exc}")
