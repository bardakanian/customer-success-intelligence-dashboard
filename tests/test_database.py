import pytest

from app.database.database import Database


def test_first_run_seeds_once_and_persists_user_entries(tmp_path):
    database_path = tmp_path / "customer_success.db"
    database = Database(database_path)

    database.initialize()
    customers = database.customers()
    assert database_path.exists()
    assert len(customers) == 30
    assert len(database.activities()) == 120

    customer_id = customers[0].id
    database.add_note(customer_id, "Test Author", "Persistent account context.")
    database.add_activity(
        customer_id,
        "Internal Note",
        "Test activity",
        "Persistent activity context.",
        "Test Author",
    )

    database.initialize()

    assert len(database.customers()) == 30
    assert len(database.activities()) == 121
    assert database.notes(customer_id)[0]["note_text"] == "Persistent account context."


def test_activity_validation_requires_owner_and_content(tmp_path):
    database = Database(tmp_path / "validation.db")
    database.initialize()
    customer_id = database.customers()[0].id

    with pytest.raises(ValueError, match="required"):
        database.add_activity(
            customer_id,
            "Internal Note",
            "",
            "",
            "",
        )
