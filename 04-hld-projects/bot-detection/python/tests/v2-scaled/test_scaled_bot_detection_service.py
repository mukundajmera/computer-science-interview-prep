import unittest
from unittest.mock import Mock, call
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_bot_detection_service import (
    ScaledBotDetectionService,
    FeatureResult,
    RuleResult,
    ModelResult,
    PolicyDecision,
    ActionType,
    ActionEvent,
    EvaluationResult
)

class TestScaledBotDetectionService(unittest.TestCase):
    def setUp(self):
        self.feature_service = Mock()
        self.rules_engine = Mock()
        self.model_service = Mock()
        self.anomaly_detector = Mock()
        self.policy_engine = Mock()
        self.deferred_analysis_service = Mock()
        self.label_store = Mock()
        self.metrics_service = Mock()
        self.action_store = Mock()

        self.policy_engine.get_policy_version.return_value = "v1"

        self.service = ScaledBotDetectionService(
            feature_service=self.feature_service,
            rules_engine=self.rules_engine,
            model_service=self.model_service,
            anomaly_detector=self.anomaly_detector,
            policy_engine=self.policy_engine,
            deferred_analysis_service=self.deferred_analysis_service,
            label_store=self.label_store,
            metrics_service=self.metrics_service,
            action_store=self.action_store,
        )

    def test_healthy_evaluation_path(self):
        # Setup
        account_id = "user123"
        features = {"login_rate": 0.5}

        self.feature_service.get_features.return_value = FeatureResult(features=features, is_delayed=False)
        self.rules_engine.evaluate.return_value = RuleResult(score=0.2, matched_high_precision=False)
        self.model_service.evaluate.return_value = ModelResult(score=0.4, timed_out=False)
        self.anomaly_detector.get_anomaly_score.return_value = 0.1
        self.policy_engine.decide_action.return_value = PolicyDecision(action=ActionType.ALLOW, reason="Low Risk")

        # Action
        result = self.service.evaluate_account(account_id)

        # Assertions
        expected_score = (0.2 * 0.3) + (0.4 * 0.5) + (0.1 * 0.2) # 0.06 + 0.20 + 0.02 = 0.28
        self.assertAlmostEqual(result.score, 0.28)
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.action, ActionType.ALLOW)

        self.feature_service.get_features.assert_called_once_with(account_id)
        self.rules_engine.evaluate.assert_called_once_with(account_id, features)
        self.model_service.evaluate.assert_called_once_with(account_id, features)
        self.anomaly_detector.get_anomaly_score.assert_called_once_with(account_id, features)
        self.policy_engine.decide_action.assert_called_once_with(expected_score, 1.0)
        self.action_store.save_action.assert_called_once()
        self.deferred_analysis_service.enqueue_for_analysis.assert_not_called()
        self.metrics_service.record_value.assert_called_once()
        self.assertEqual(self.metrics_service.record_value.call_args[0][0], "evaluation.latency.ms")

    def test_healthy_evaluation_matched_high_precision(self):
        account_id = "user123"
        features = {"login_rate": 0.5}

        self.feature_service.get_features.return_value = FeatureResult(features=features, is_delayed=False)
        self.rules_engine.evaluate.return_value = RuleResult(score=0.2, matched_high_precision=True)
        self.model_service.evaluate.return_value = ModelResult(score=0.4, timed_out=False)
        self.anomaly_detector.get_anomaly_score.return_value = 0.1
        self.policy_engine.decide_action.return_value = PolicyDecision(action=ActionType.SUSPEND, reason="High Risk")

        result = self.service.evaluate_account(account_id)

        # The base score is 0.28, but matched_high_precision is True, so it should be max(0.28, 0.9)
        self.assertAlmostEqual(result.score, 0.9)

    def test_degraded_mode_model_timeout_high_precision_rule(self):
        account_id = "user456"
        features = {"spam_count": 10.0}

        self.feature_service.get_features.return_value = FeatureResult(features=features, is_delayed=False)
        self.rules_engine.evaluate.return_value = RuleResult(score=0.8, matched_high_precision=True)
        self.model_service.evaluate.return_value = ModelResult(score=0.0, timed_out=True)
        self.policy_engine.decide_action.return_value = PolicyDecision(action=ActionType.SUSPEND, reason="High Precision Match in degraded mode")

        result = self.service.evaluate_account(account_id)

        self.assertEqual(result.score, 0.9)
        self.assertAlmostEqual(result.confidence, 0.6) # 1.0 - 0.4
        self.assertEqual(result.action, ActionType.SUSPEND)

        self.metrics_service.increment.assert_any_call("model.timeout.degraded_mode")
        self.deferred_analysis_service.enqueue_for_analysis.assert_called_with(account_id, features)
        self.anomaly_detector.get_anomaly_score.assert_not_called()

    def test_degraded_mode_model_timeout_low_precision_rule(self):
        account_id = "user789"
        features = {"spam_count": 2.0}

        self.feature_service.get_features.return_value = FeatureResult(features=features, is_delayed=False)
        self.rules_engine.evaluate.return_value = RuleResult(score=0.4, matched_high_precision=False)
        self.model_service.evaluate.return_value = ModelResult(score=0.0, timed_out=True)
        self.policy_engine.decide_action.return_value = PolicyDecision(action=ActionType.CHALLENGE, reason="Medium Risk in degraded mode")

        result = self.service.evaluate_account(account_id)

        self.assertEqual(result.score, 0.4)
        self.assertAlmostEqual(result.confidence, 0.6)

    def test_delayed_features_lower_confidence(self):
        account_id = "user999"
        features = {"some_feature": 1.0}

        self.feature_service.get_features.return_value = FeatureResult(features=features, is_delayed=True)
        self.rules_engine.evaluate.return_value = RuleResult(score=0.1, matched_high_precision=False)
        self.model_service.evaluate.return_value = ModelResult(score=0.1, timed_out=False)
        self.anomaly_detector.get_anomaly_score.return_value = 0.1
        self.policy_engine.decide_action.return_value = PolicyDecision(action=ActionType.ROUTE_TO_REVIEW, reason="Low confidence route")

        result = self.service.evaluate_account(account_id)

        self.assertAlmostEqual(result.confidence, 0.7) # 1.0 - 0.3
        self.assertEqual(result.action, ActionType.ROUTE_TO_REVIEW)
        self.metrics_service.increment.assert_any_call("features.delayed")
        # Confidence < 0.8 should trigger deferred analysis
        self.deferred_analysis_service.enqueue_for_analysis.assert_called_with(account_id, features)

    def test_investigator_label_accepted(self):
        account_id = "user111"
        label = "bot"
        agreement_score = 0.9 # >= 0.8

        self.service.submit_investigator_label(account_id, label, agreement_score)

        self.metrics_service.increment.assert_called_with("label.accepted")
        self.label_store.save_label.assert_called_once_with(account_id, label, agreement_score, False)

    def test_investigator_label_holdback(self):
        account_id = "user222"
        label = "human"
        agreement_score = 0.5 # < 0.8

        self.service.submit_investigator_label(account_id, label, agreement_score)

        self.metrics_service.increment.assert_called_with("label.held_back")
        self.label_store.save_label.assert_called_once_with(account_id, label, agreement_score, True)

if __name__ == '__main__':
    unittest.main()
