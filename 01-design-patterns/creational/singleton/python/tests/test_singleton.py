import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
from singleton import Singleton, DatabaseConnection


@pytest.fixture(autouse=True)
def reset_singleton():
    Singleton._instance = None
    yield
    Singleton._instance = None


def test_singleton_returns_same_instance():
    s1 = Singleton()
    s2 = Singleton()
    assert s1 is s2


def test_singleton_state_shared():
    s1 = Singleton()
    s2 = Singleton()
    s1.set_value("shared_state")
    assert s2.get_value() == "shared_state"


def test_database_connection_singleton_lifecycle():
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    assert db1 is db2

    db1.connect()
    assert db2.connected is True
    res = db1.execute_query("SELECT 1")
    assert "SELECT 1" in res

    db2.disconnect()
    assert db1.connected is False
    with pytest.raises(RuntimeError):
        db1.execute_query("SELECT 1")
