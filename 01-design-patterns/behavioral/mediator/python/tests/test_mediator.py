import os
import sys
from pathlib import Path
import importlib.util
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


med_v1 = load_module("med_v1", "python/v1-basic/mediator_demo.py")
dialog = load_module("dialog", "python/v2-variant/dialog_mediator.py")
broker = load_module("broker", "python/v3-advanced/service_broker_mediator.py")


class RecordingUser(med_v1.User):
    def __init__(self, mediator, name):
        super().__init__(mediator, name)
        self.received = []

    def send(self, message: str) -> None:
        self._mediator.send_message(message, self)

    def receive(self, message: str, from_user: str) -> None:
        self.received.append((from_user, message))


def test_user_broadcasts_to_others():
    room = med_v1.ChatRoom()
    u1 = RecordingUser(room, "User1")
    u2 = RecordingUser(room, "User2")
    room.add_user(u1)
    room.add_user(u2)

    u1.send("Hello world")
    assert len(u2.received) == 1
    assert u2.received[0] == ("User1", "Hello world")


def test_sender_does_not_receive_own_message():
    room = med_v1.ChatRoom()
    u1 = RecordingUser(room, "User1")
    u2 = RecordingUser(room, "User2")
    room.add_user(u1)
    room.add_user(u2)

    u1.send("Ping")
    assert len(u1.received) == 0


def test_chat_room_multiple_users():
    room = med_v1.ChatRoom()
    alice = RecordingUser(room, "Alice")
    bob = RecordingUser(room, "Bob")
    charlie = RecordingUser(room, "Charlie")

    room.add_user(alice)
    room.add_user(bob)
    room.add_user(charlie)

    alice.send("Team meeting at 10")
    assert len(bob.received) == 1
    assert len(charlie.received) == 1
    assert bob.received[0] == ("Alice", "Team meeting at 10")
    assert charlie.received[0] == ("Alice", "Team meeting at 10")


# --- v2-variant Tests ---

def test_dialog_mediator_form_validation():
    dlg = dialog.AuthenticationDialogMediator()
    assert dlg.submit_button.enabled is False

    dlg.username_box.text = "john_doe"
    assert dlg.submit_button.enabled is False

    dlg.password_box.text = "secret123"
    assert dlg.submit_button.enabled is False

    dlg.terms_checkbox.checked = True
    assert dlg.submit_button.enabled is True

    # Clicking triggers submit via mediator
    dlg.submit_button.click()
    assert dlg.submitted is True

    # Clearing username disables submit again
    dlg.username_box.text = ""
    assert dlg.submit_button.enabled is False


# --- v3-advanced Tests ---

def test_service_broker_mediator_event_flow():
    brk = broker.ServiceBroker()
    order_svc = broker.OrderService()
    inv_svc = broker.InventoryService()
    pay_svc = broker.PaymentService()
    notif_svc = broker.NotificationService()

    brk.subscribe("ORDER_CREATED", inv_svc)
    brk.subscribe("INVENTORY_RESERVED", pay_svc)
    brk.subscribe("PAYMENT_COMPLETED", notif_svc)

    order_svc.create_order(brk, "ORD-101", 89.50)

    assert "ORD-101" in order_svc.created_orders
    assert "ORD-101" in inv_svc.reserved_orders
    assert "ORD-101" in pay_svc.processed_payments
    assert len(notif_svc.notifications) == 1
    assert "ORD-101" in notif_svc.notifications[0]

    assert brk.count_events_by_type("ORDER_CREATED") == 1
    assert brk.count_events_by_type("INVENTORY_RESERVED") == 1
    assert brk.count_events_by_type("PAYMENT_COMPLETED") == 1
    assert len(brk.history) == 3
