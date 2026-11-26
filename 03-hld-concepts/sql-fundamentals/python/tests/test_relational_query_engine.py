import pytest
import sys
import os

# Allow dynamic imports from v1-simple without modifying global PYTHONPATH manually.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from relational_query_engine import Column, Table, Database

def test_insert_and_select():
    db = Database()
    users_table = Table("users", [
        Column("id", int, primary_key=True),
        Column("name", str),
        Column("age", int)
    ])
    db.create_table(users_table)

    db.insert("users", {"id": 1, "name": "Alice", "age": 30})
    db.insert("users", {"id": 2, "name": "Bob", "age": 25})

    # Select all
    all_users = db.select("users")
    assert len(all_users) == 2

    # Select with predicate
    bobs = db.select("users", lambda r: r["name"] == "Bob")
    assert len(bobs) == 1
    assert bobs[0]["age"] == 25

def test_constraints_validation():
    db = Database()
    users_table = Table("users", [
        Column("id", int, primary_key=True),
        Column("email", str, unique=True)
    ])
    db.create_table(users_table)

    # Missing PK
    with pytest.raises(ValueError, match="cannot be null"):
        db.insert("users", {"email": "alice@example.com"})

    # Type mismatch
    with pytest.raises(ValueError, match="expects int, got str"):
        db.insert("users", {"id": "1", "email": "alice@example.com"})

    db.insert("users", {"id": 1, "email": "alice@example.com"})

    # Unique constraint violation
    with pytest.raises(ValueError, match="Unique constraint failed"):
        db.insert("users", {"id": 2, "email": "alice@example.com"})

    # PK constraint violation
    with pytest.raises(ValueError, match="Unique constraint failed"):
        db.insert("users", {"id": 1, "email": "bob@example.com"})

def test_update_and_delete():
    db = Database()
    users_table = Table("users", [
        Column("id", int, primary_key=True),
        Column("status", str)
    ])
    db.create_table(users_table)

    db.insert("users", {"id": 1, "status": "active"})
    db.insert("users", {"id": 2, "status": "inactive"})

    # Update
    db.update("users", lambda r: r["id"] == 2, {"status": "active"})
    user2 = db.select("users", lambda r: r["id"] == 2)[0]
    assert user2["status"] == "active"

    # Delete
    db.delete("users", lambda r: r["id"] == 1)
    all_users = db.select("users")
    assert len(all_users) == 1
    assert all_users[0]["id"] == 2

def test_inner_join_and_group_by():
    db = Database()
    users = Table("users", [Column("id", int, primary_key=True), Column("department", str)])
    db.create_table(users)
    orders = Table("orders", [Column("id", int, primary_key=True), Column("user_id", int), Column("amount", float)])
    db.create_table(orders)

    db.insert("users", {"id": 1, "department": "Sales"})
    db.insert("users", {"id": 2, "department": "Marketing"})

    db.insert("orders", {"id": 101, "user_id": 1, "amount": 100.0})
    db.insert("orders", {"id": 102, "user_id": 1, "amount": 250.0})
    db.insert("orders", {"id": 103, "user_id": 2, "amount": 50.0})

    # Join
    joined = db.inner_join("users", "orders", lambda u, o: u["id"] == o["user_id"])
    assert len(joined) == 3
    assert joined[0]["users.department"] == "Sales"
    assert joined[0]["orders.amount"] == 100.0

    # Group by COUNT
    count_grouped = db.group_by("orders", ["user_id"], "id", "COUNT")
    assert len(count_grouped) == 2
    for row in count_grouped:
        if row["user_id"] == 1:
            assert row["COUNT(id)"] == 2
        elif row["user_id"] == 2:
            assert row["COUNT(id)"] == 1

    # Group by SUM
    sum_grouped = db.group_by("orders", ["user_id"], "amount", "SUM")
    for row in sum_grouped:
        if row["user_id"] == 1:
            assert row["SUM(amount)"] == 350.0
        elif row["user_id"] == 2:
            assert row["SUM(amount)"] == 50.0
