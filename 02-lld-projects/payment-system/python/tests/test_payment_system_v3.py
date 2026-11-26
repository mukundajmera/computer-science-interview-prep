import unittest
import sys
import os

# Add v3-optimized to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v3-optimized')))

from payment_service import PaymentService, PaymentRequest, TransactionState

class TestV3(unittest.TestCase):
    def setUp(self):
        self.service = PaymentService()

    def test_v3_sanity(self) -> None:
        self.assertIsNotNone("ok")

    def test_idempotency_key_repeat(self):
        req = PaymentRequest("uuid-123", 1000, "USD", "tok_1")
        resp1 = self.service.process_payment(req)
        self.assertEqual(resp1["status"], "SUCCESS")
        
        # Second identical request should return the same response
        resp2 = self.service.process_payment(req)
        self.assertEqual(resp2, resp1)
        
        # Check that only one transaction was created
        self.assertEqual(len(self.service.transactions), 1)

    def test_idempotency_key_payload_mismatch(self):
        req1 = PaymentRequest("uuid-456", 1000, "USD", "tok_1")
        self.service.process_payment(req1)
        
        req2 = PaymentRequest("uuid-456", 2000, "USD", "tok_1")
        with self.assertRaises(ValueError):
            self.service.process_payment(req2)

    def test_gateway_timeout_and_webhook_reconciliation(self):
        # 3000 causes timeout
        req = PaymentRequest("uuid-789", 3000, "USD", "tok_2")
        resp = self.service.process_payment(req)
        self.assertEqual(resp["status"], "PENDING")
        tx_id = resp["transaction_id"]
        
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.GATEWAY_PENDING)
        
        # Webhook arrives
        self.service.handle_webhook(tx_id, "COMPLETED")
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.COMPLETED)
        
        # Duplicate webhook arrives
        self.service.handle_webhook(tx_id, "DECLINED")
        # Should remain COMPLETED
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.COMPLETED)

    def test_gateway_declined(self):
        # 2000 causes declined
        req = PaymentRequest("uuid-999", 2000, "USD", "tok_3")
        resp = self.service.process_payment(req)
        self.assertEqual(resp["status"], "DECLINED")
        tx_id = resp["transaction_id"]
        
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.DECLINED)

    def test_rollback_fixture(self):
        # 4000 causes exception
        req = PaymentRequest("uuid-rollback", 4000, "USD", "tok_rollback")
        resp = self.service.process_payment(req)
        self.assertEqual(resp["status"], "FAILED")
        tx_id = resp["transaction_id"]
        
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.FAILED)
        
        # Webhook arriving late for FAILED should be ignored
        self.service.handle_webhook(tx_id, "COMPLETED")
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.FAILED)

    def test_out_of_order_webhook_delivery(self):
        req = PaymentRequest("uuid-ooo", 3000, "USD", "tok_ooo")
        resp = self.service.process_payment(req)
        self.assertEqual(resp["status"], "PENDING")
        tx_id = resp["transaction_id"]

        self.service.handle_webhook(tx_id, "COMPLETED")
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.COMPLETED)
        
        self.service.handle_webhook(tx_id, "DECLINED")
        self.assertEqual(self.service.transactions[tx_id].state, TransactionState.COMPLETED)

if __name__ == "__main__":
    unittest.main()
