import pytest
import os
import sys

# Memory: Python tests in this repository require dynamic sys.path imports. To avoid ImportErrors with hyphenated directories, use os.path.abspath when inserting all required version directories into the path.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))
)

from streaming_filter import StreamingSafetyInspector, PolicyViolationError
from canary_calibrator import BayesianEstimator, RollbackPolicyManager, CanaryCalibrationRouter

def test_streaming_filter_safe():
    inspector = StreamingSafetyInspector(block_patterns=["toxic", "unsafe"])
    stream = iter(["This ", "is ", "a ", "safe ", "stream."])

    # Should not raise exception
    tokens = list(inspector.inspect_stream(stream))
    assert tokens == ["This ", "is ", "a ", "safe ", "stream."]

def test_streaming_filter_violation():
    inspector = StreamingSafetyInspector(block_patterns=["toxic", "unsafe"])
    stream = iter(["This ", "is ", "toxic ", "behavior."])

    with pytest.raises(PolicyViolationError) as exc_info:
        list(inspector.inspect_stream(stream))

    assert "toxic" in str(exc_info.value)

def test_bayesian_estimator_updates():
    estimator = BayesianEstimator(initial_threshold=0.5, prior_alpha=1, prior_beta=1)

    assert estimator.get_estimated_fp_rate() == 0.5

    estimator.observe(false_positive=True)
    # alpha=2, beta=1 -> 2/3
    assert abs(estimator.get_estimated_fp_rate() - (2/3)) < 1e-5

    estimator.observe(false_positive=False)
    # alpha=2, beta=2 -> 2/4 = 0.5
    assert estimator.get_estimated_fp_rate() == 0.5

def test_bayesian_estimator_adjust_threshold():
    estimator = BayesianEstimator(initial_threshold=0.5, prior_alpha=5, prior_beta=1)
    # high fp rate: 5/6 = 0.833
    target = 0.1
    new_threshold = estimator.adjust_threshold(target)
    # 0.5 + 0.05 = 0.55
    assert new_threshold == 0.55

    estimator = BayesianEstimator(initial_threshold=0.5, prior_alpha=1, prior_beta=100)
    # very low fp rate
    target = 0.5
    new_threshold = estimator.adjust_threshold(target)
    # 0.5 - 0.05 = 0.45
    assert new_threshold == 0.45

def test_rollback_policy_manager():
    manager = RollbackPolicyManager()

    manager.deploy({"policy1": "v1"})
    assert manager.active_policies == {"policy1": "v1"}

    manager.deploy({"policy1": "v2"})
    assert manager.active_policies == {"policy1": "v2"}

    manager.rollback()
    assert manager.active_policies == {"policy1": "v1"}

    manager.rollback()
    assert manager.active_policies == {}

def test_canary_routing_and_auto_abort():
    manager = RollbackPolicyManager()
    manager.deploy({"active": "stable"})
    manager.deploy({"active": "canary"})

    estimator = BayesianEstimator(prior_alpha=1, prior_beta=9) # FP rate 0.1
    router = CanaryCalibrationRouter(manager, estimator, max_fp_rate=0.2, canary_fraction=0.5)

    # 1st request -> stable
    assert router.route_request("text") == "stable"
    # 2nd request -> canary
    assert router.route_request("text") == "canary"

    # Observe many false positives
    for _ in range(5):
        estimator.observe(True)

    # FP rate is now 6 / 15 = 0.4, which > max_fp_rate (0.2)
    assert router.route_request("text") == "stable"
    assert manager.active_policies == {"active": "stable"} # Rolled back!