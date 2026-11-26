"""
Tests for State Pattern implementations.
"""
import os
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-pythonic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-advanced"))


class TestV1VendingMachineState(unittest.TestCase):
    """Tests for V1 Basic Vending Machine State."""

    def test_paid_selection_dispenses_and_returns_to_idle(self):
        """Selecting with enough balance should dispense and reset."""
        from state_demo import IdleState, VendingMachine

        machine = VendingMachine()

        machine.insert_money(1.00)
        machine.insert_money(0.50)
        machine.select_product()

        self.assertEqual(machine.balance, 0)
        self.assertIsInstance(machine._state, IdleState)


class TestV2OrderState(unittest.TestCase):
    """Tests for V2 Pythonic Order State."""

    def test_paid_order_can_ship_and_deliver(self):
        """Order should move through paid, shipped, delivered states."""
        from order_state import DeliveredState, Order

        order = Order("order-1001")

        order.pay("card")
        order.ship("TRK-1")
        order.deliver()

        self.assertIsInstance(order.state, DeliveredState)
        self.assertEqual(order.status, "DELIVERED")
        self.assertEqual(order.tracking_number, "TRK-1")
        self.assertEqual(order.history, ["CREATED", "PAID", "SHIPPED", "DELIVERED"])

    def test_shipped_order_cannot_be_cancelled(self):
        """State object should reject cancellation after shipment."""
        from order_state import Order

        order = Order("order-1002")
        order.pay("wallet")
        order.ship("TRK-2")

        with self.assertRaisesRegex(ValueError, "Cannot cancel"):
            order.cancel("buyer changed mind")


class TestV3DocumentWorkflowState(unittest.TestCase):
    """Tests for V3 Advanced Document Workflow State."""

    def test_document_requires_approval_before_publish(self):
        """Document should enforce review before publication."""
        from document_workflow import DocumentWorkflow, PublishedState

        document = DocumentWorkflow("design-doc")

        document.submit_for_review("alice")
        with self.assertRaisesRegex(ValueError, "approval"):
            document.publish("alice")

        document.approve("lead")
        document.publish("alice")

        self.assertIsInstance(document.state, PublishedState)
        self.assertEqual(document.status, "PUBLISHED")
        self.assertEqual(document.approvals, ["lead"])

    def test_published_document_can_be_archived_but_not_edited(self):
        """Published documents should lock edits and allow archival."""
        from document_workflow import ArchivedState, DocumentWorkflow

        document = DocumentWorkflow("api-contract")
        document.edit("initial content")
        document.submit_for_review("alice")
        document.approve("lead")
        document.publish("alice")

        with self.assertRaisesRegex(ValueError, "published"):
            document.edit("breaking rewrite")

        document.archive("superseded")

        self.assertIsInstance(document.state, ArchivedState)
        self.assertEqual(document.archive_reason, "superseded")


if __name__ == "__main__":
    unittest.main()
