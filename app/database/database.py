"""SQLite persistence and query layer."""

from __future__ import annotations

import sqlite3
from dataclasses import fields
from datetime import date
from pathlib import Path

from app.database.models import Customer
from app.database.seed import activity_history, build_customers
from app.services.health_service import enrich_health
from app.services.risk_service import calculate_risk_level

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "customer_success.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT UNIQUE NOT NULL,
    industry TEXT NOT NULL,
    account_owner TEXT NOT NULL,
    customer_tier TEXT NOT NULL,
    annual_recurring_revenue REAL NOT NULL,
    contract_start_date TEXT NOT NULL,
    renewal_date TEXT NOT NULL,
    monthly_active_users INTEGER NOT NULL,
    licensed_users INTEGER NOT NULL,
    usage_change_30d REAL NOT NULL,
    open_support_tickets INTEGER NOT NULL,
    critical_tickets INTEGER NOT NULL,
    average_ticket_resolution_hours REAL NOT NULL,
    customer_satisfaction_score REAL NOT NULL,
    nps_score INTEGER NOT NULL,
    last_meeting_date TEXT NOT NULL,
    executive_sponsor TEXT NOT NULL,
    primary_contact TEXT NOT NULL,
    product_adoption_score REAL NOT NULL,
    engagement_score REAL NOT NULL,
    sentiment_score REAL NOT NULL,
    health_score REAL NOT NULL DEFAULT 0,
    health_category TEXT NOT NULL DEFAULT 'Critical',
    support_score REAL NOT NULL DEFAULT 0,
    risk_level TEXT NOT NULL DEFAULT 'Low'
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    activity_date TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    owner TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    note_date TEXT NOT NULL,
    author TEXT NOT NULL,
    note_text TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_customers_renewal
    ON customers(renewal_date);
CREATE INDEX IF NOT EXISTS idx_activities_customer
    ON activities(customer_id);
"""


class Database:
    """Own database initialization and the application's small query surface."""

    def __init__(self, path: str | Path = DEFAULT_DATABASE_PATH):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create the schema, seed an empty database, and refresh derived fields."""
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            customer_count = connection.execute(
                "SELECT COUNT(*) FROM customers"
            ).fetchone()[0]
            if customer_count == 0:
                self._seed(connection)

        # Renewal proximity changes with time, so risk fields are refreshed on launch.
        self.refresh_scores()

    def _seed(self, connection: sqlite3.Connection) -> None:
        customer_fields = [
            field.name for field in fields(Customer) if field.name != "id"
        ]
        placeholders = ",".join("?" for _ in customer_fields)
        insert_customer = (
            f"INSERT INTO customers ({','.join(customer_fields)}) "
            f"VALUES ({placeholders})"
        )
        insert_activity = """
            INSERT INTO activities (
                customer_id, activity_date, activity_type, title, description, owner
            ) VALUES (?, ?, ?, ?, ?, ?)
        """

        for customer in build_customers():
            values = [getattr(customer, field) for field in customer_fields]
            cursor = connection.execute(insert_customer, values)
            connection.executemany(
                insert_activity,
                activity_history(cursor.lastrowid, customer.account_owner),
            )

    def refresh_scores(self) -> None:
        customers = self.customers()
        with self.connect() as connection:
            for customer in customers:
                enrich_health(customer)
                customer.risk_level = calculate_risk_level(customer)
                connection.execute(
                    """
                    UPDATE customers
                    SET health_score = ?, health_category = ?,
                        support_score = ?, risk_level = ?
                    WHERE id = ?
                    """,
                    (
                        customer.health_score,
                        customer.health_category,
                        customer.support_score,
                        customer.risk_level,
                        customer.id,
                    ),
                )

    def customers(self) -> list[Customer]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM customers ORDER BY company_name"
            )
            return [Customer.from_row(row) for row in rows]

    def customer(self, customer_id: int) -> Customer | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,),
            ).fetchone()
            return Customer.from_row(row) if row else None

    def activities(self, customer_id: int | None = None) -> list[sqlite3.Row]:
        query = """
            SELECT a.*, c.company_name
            FROM activities AS a
            JOIN customers AS c ON c.id = a.customer_id
        """
        parameters: tuple[int, ...] = ()
        if customer_id is not None:
            query += " WHERE a.customer_id = ?"
            parameters = (customer_id,)
        query += " ORDER BY a.activity_date DESC, a.id DESC"
        with self.connect() as connection:
            return list(connection.execute(query, parameters))

    def notes(self, customer_id: int) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT * FROM notes
                    WHERE customer_id = ?
                    ORDER BY note_date DESC, id DESC
                    """,
                    (customer_id,),
                )
            )

    def add_activity(
        self,
        customer_id: int,
        activity_type: str,
        title: str,
        description: str,
        owner: str,
        activity_date: str | None = None,
    ) -> None:
        if not title.strip() or not description.strip() or not owner.strip():
            raise ValueError("Owner, title, and description are required.")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO activities (
                    customer_id, activity_date, activity_type, title, description, owner
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    activity_date or date.today().isoformat(),
                    activity_type,
                    title.strip(),
                    description.strip(),
                    owner.strip(),
                ),
            )

    def add_note(
        self,
        customer_id: int,
        author: str,
        text: str,
        note_date: str | None = None,
    ) -> None:
        if not text.strip():
            raise ValueError("Note text is required.")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO notes (customer_id, note_date, author, note_text)
                VALUES (?, ?, ?, ?)
                """,
                (
                    customer_id,
                    note_date or date.today().isoformat(),
                    author.strip() or "Account Team",
                    text.strip(),
                ),
            )
