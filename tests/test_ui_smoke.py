"""Headless integration coverage for the primary desktop workflows."""

from __future__ import annotations

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.database.database import Database
from app.ui.dialogs import EntryDialog
from app.ui.main_window import MainWindow


def _complete_entry_dialog(mode: str) -> None:
    dialog = QApplication.activeModalWidget()
    assert isinstance(dialog, EntryDialog)
    if mode == "Activity":
        dialog.title.setText("Release audit account review")
        dialog.text.setPlainText("Confirmed customer priorities and documented next steps.")
    else:
        dialog.text.setPlainText("Release audit note persisted through the Customer 360 workflow.")
    dialog.validate_and_accept()


def test_primary_ui_workflows_and_persistence(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    database_path = tmp_path / "release-smoke.db"
    database = Database(database_path)
    database.initialize()
    window = MainWindow(database)
    window.show()
    app.processEvents()

    assert len(database.customers()) == 30
    assert len(database.activities()) == 120

    for page_index in range(6):
        window.navigate(page_index)
        app.processEvents()
        assert window.stack.currentWidget() is window.pages[page_index]

    window.accounts.search.setText("logistics")
    assert window.accounts.table.rowCount() >= 1
    window.accounts.search.setText("no-account-matches-this-query")
    assert window.accounts.table.rowCount() == 0
    window.accounts.reset_filters()
    for combo in (
        window.accounts.health,
        window.accounts.risk,
        window.accounts.tier,
        window.accounts.industry,
        window.accounts.renewal,
    ):
        combo.setCurrentIndex(min(1, combo.count() - 1))
        app.processEvents()
        combo.setCurrentIndex(0)

    for checkbox in (
        window.risks.high_arr,
        window.risks.renewal,
        window.risks.critical,
        window.risks.decline,
    ):
        checkbox.setChecked(True)
        app.processEvents()
        checkbox.setChecked(False)

    for button in window.renewals.window_buttons:
        button.click()
        app.processEvents()
        assert window.renewals.selected_days() == button.property("days")

    window.activities.search.setText("customer")
    window.activities.kind.setCurrentIndex(1)
    app.processEvents()
    window.activities.reset_filters()
    assert window.activities.table.rowCount() == 120

    customers = database.customers()
    for customer in (customers[0], min(customers, key=lambda item: item.health_score)):
        window.open_account(customer.id)
        app.processEvents()
        assert window.detail.customer_id == customer.id

    customer = customers[0]
    initial_activity_count = len(database.activities(customer.id))
    QTimer.singleShot(0, lambda: _complete_entry_dialog("Activity"))
    window.detail._add("Activity", customer)
    assert len(database.activities(customer.id)) == initial_activity_count + 1

    initial_note_count = len(database.notes(customer.id))
    QTimer.singleShot(0, lambda: _complete_entry_dialog("Note"))
    window.detail._add("Note", customer)
    assert len(database.notes(customer.id)) == initial_note_count + 1

    window.apply_theme("dark")
    assert window.theme == "dark"
    window.apply_theme("light")
    assert window.theme == "light"
    for width, height in ((1100, 700), (1440, 900)):
        window.resize(width, height)
        app.processEvents()
        assert window.size().width() >= width
        assert window.size().height() >= height

    reopened = Database(database_path)
    reopened.initialize()
    assert len(reopened.customers()) == 30
    assert len(reopened.activities(customer.id)) == initial_activity_count + 1
    assert len(reopened.notes(customer.id)) == initial_note_count + 1
    window.close()
