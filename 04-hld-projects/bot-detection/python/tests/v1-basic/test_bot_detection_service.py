import unittest
import sys
import os
from datetime import datetime, timezone

# Add the source directory to the path dynamically
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from bot_detection_service import (
    BotDetectionService,
    BehaviorSignal,
    RiskState,
    ActionType
)

class TestBotDetectionService(unittest.TestCase):
    def setUp(self):
        self.service = BotDetectionService()

    def test_evaluate_account_active(self):
        signals = [
            BehaviorSignal(account_id="user1", signal_type="failed_logins", signal_value=1.0, event_time=datetime.now(timezone.utc))
        ]
        state = self.service.evaluate_account("user1", signals)
        self.assertEqual(state.state, RiskState.ACTIVE)
        self.assertEqual(state.score, 10.0)

    def test_evaluate_account_challenge(self):
        signals = [
            BehaviorSignal(account_id="user2", signal_type="failed_logins", signal_value=6.0, event_time=datetime.now(timezone.utc))
        ]
        state = self.service.evaluate_account("user2", signals)
        self.assertEqual(state.state, RiskState.CHALLENGED)
        self.assertEqual(state.score, 60.0)

    def test_evaluate_account_limit(self):
        signals = [
            BehaviorSignal(account_id="user3", signal_type="failed_logins", signal_value=8.0, event_time=datetime.now(timezone.utc))
        ]
        state = self.service.evaluate_account("user3", signals)
        self.assertEqual(state.state, RiskState.LIMITED)
        self.assertEqual(state.score, 80.0)

    def test_evaluate_account_suspend(self):
        signals = [
            BehaviorSignal(account_id="user4", signal_type="bot_signature", signal_value=2.0, event_time=datetime.now(timezone.utc))
        ]
        state = self.service.evaluate_account("user4", signals)
        self.assertEqual(state.state, RiskState.SUSPENDED)
        self.assertEqual(state.score, 100.0)

    def test_submit_appeal(self):
        self.service.evaluate_account("user5", [])
        success = self.service.submit_appeal("user5", "I am human")
        self.assertTrue(success)
        self.assertEqual(len(self.service.appeals), 1)

    def test_submit_investigator_label_restore(self):
        signals = [
            BehaviorSignal(account_id="user6", signal_type="bot_signature", signal_value=2.0, event_time=datetime.now(timezone.utc))
        ]
        self.service.evaluate_account("user6", signals)
        self.assertEqual(self.service.get_account_status("user6").state, RiskState.SUSPENDED)

        self.service.submit_investigator_label("user6", "legitimate", 0.9)
        self.assertEqual(self.service.get_account_status("user6").state, RiskState.ACTIVE)
        self.assertEqual(self.service.get_account_status("user6").score, 0.0)

    def test_get_metrics(self):
        self.service.evaluate_account("user7", [BehaviorSignal(account_id="user7", signal_type="failed_logins", signal_value=1.0, event_time=datetime.now(timezone.utc))])
        self.service.evaluate_account("user8", [BehaviorSignal(account_id="user8", signal_type="bot_signature", signal_value=2.0, event_time=datetime.now(timezone.utc))])

        metrics = self.service.get_metrics()
        self.assertEqual(metrics["total_evaluated"], 2)
        self.assertEqual(metrics["active"], 1)
        self.assertEqual(metrics["suspended"], 1)

    def test_evaluate_account_empty_signals(self):
        state = self.service.evaluate_account("user9", [])
        self.assertEqual(state.state, RiskState.ACTIVE)
        self.assertEqual(state.score, 0.0)

    def test_evaluate_account_escalation(self):
        # Evaluate first time -> challenge
        signals1 = [BehaviorSignal(account_id="user10", signal_type="failed_logins", signal_value=6.0, event_time=datetime.now(timezone.utc))]
        state1 = self.service.evaluate_account("user10", signals1)
        self.assertEqual(state1.state, RiskState.CHALLENGED)

        # Evaluate second time -> suspend
        signals2 = [
            BehaviorSignal(account_id="user10", signal_type="bot_signature", signal_value=2.0, event_time=datetime.now(timezone.utc)),
            BehaviorSignal(account_id="user10", signal_type="rapid_messages", signal_value=5.0, event_time=datetime.now(timezone.utc))
        ]
        state2 = self.service.evaluate_account("user10", signals2)
        self.assertEqual(state2.state, RiskState.SUSPENDED)

        status = self.service.get_account_status("user10")
        self.assertEqual(status.state, RiskState.SUSPENDED)

    def test_submit_appeal_invalid_account(self):
        success = self.service.submit_appeal("unknown_user", "I am a human")
        self.assertFalse(success)
        self.assertEqual(len(self.service.appeals), 0)

if __name__ == '__main__':
    unittest.main()
