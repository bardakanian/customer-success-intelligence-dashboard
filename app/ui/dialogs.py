"""Validated data-entry dialogs."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

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


class EntryDialog(QDialog):
    """Collect and validate a new account activity or note."""

    def __init__(self, mode: str, owner: str, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle(f"Add {mode}")
        self.setMinimumSize(500, 390 if mode == "Activity" else 330)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(14)
        title = QLabel(f"Add {mode.lower()}")
        title.setObjectName("title")
        subtitle = QLabel(
            "Capture clear context so the full account team can follow the customer history."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(subtitle)

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(11)
        self.owner = QLineEdit(owner)
        self.owner.setPlaceholderText("Account team member")
        form.addRow("Owner / author", self.owner)

        if mode == "Activity":
            self.kind = QComboBox()
            self.kind.addItems(ACTIVITY_TYPES)
            form.addRow("Activity type", self.kind)
            self.title = QLineEdit()
            self.title.setPlaceholderText("Concise activity title")
            form.addRow("Title", self.title)

        self.text = QTextEdit()
        self.text.setMinimumHeight(110)
        placeholder = (
            "Capture context, decisions, and next steps…"
            if mode == "Activity"
            else "Write an account note…"
        )
        self.text.setPlaceholderText(placeholder)
        form.addRow("Description" if mode == "Activity" else "Note", self.text)
        root.addLayout(form)

        self.error = QLabel()
        self.error.setStyleSheet("color:#C94747; font-weight:600;")
        self.error.hide()
        root.addWidget(self.error)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Save
        )
        save = buttons.button(QDialogButtonBox.Save)
        cancel = buttons.button(QDialogButtonBox.Cancel)
        save.setObjectName("primary")
        save.setText(f"Save {mode.lower()}")
        cancel.setObjectName("secondary")
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        if mode == "Activity":
            self.title.setFocus()
        else:
            self.text.setFocus()

    def validate_and_accept(self) -> None:
        missing = []
        if not self.owner.text().strip():
            missing.append("owner or author")
        if self.mode == "Activity" and not self.title.text().strip():
            missing.append("title")
        if not self.text.toPlainText().strip():
            missing.append(
                "description" if self.mode == "Activity" else "note text"
            )
        if missing:
            self.error.setText("Please provide " + ", ".join(missing) + ".")
            self.error.show()
            return
        self.accept()
