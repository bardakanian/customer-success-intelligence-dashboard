"""Application entry point for the Customer Success Intelligence Dashboard."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.database.database import Database
from app.ui.main_window import MainWindow


def main() -> int:
    """Initialize the local data store and run the desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Customer Success Intelligence Dashboard")
    app.setOrganizationName("Portfolio Labs")

    database = Database()
    database.initialize()

    window = MainWindow(database)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
