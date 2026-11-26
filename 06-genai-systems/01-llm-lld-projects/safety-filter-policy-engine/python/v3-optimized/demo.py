"""
Demo script for v3-optimized safety filter policy engine.
"""

from streaming_filter import StreamingSafetyInspector, PolicyViolationError
from canary_calibrator import BayesianEstimator, RollbackPolicyManager, CanaryCalibrationRouter

def demo_streaming_filter():
    print("--- Streaming Filter Demo ---")
    inspector = StreamingSafetyInspector(block_patterns=["badword", "unsafe"])

    stream1 = iter(["This ", "is ", "a ", "safe ", "sentence."])
    print("Evaluating safe stream:")
    for token in inspector.inspect_stream(stream1):
        print(f"Yielded: {token}", end="")
    print("\nStream 1 finished safely.\n")

    stream2 = iter(["This ", "contains ", "a ", "badword ", "here."])
    print("Evaluating unsafe stream:")
    try:
        for token in inspector.inspect_stream(stream2):
            print(f"Yielded: {token}", end="")
    except PolicyViolationError as e:
        print(f"\nCaught Exception: {e}")
    print("\n")


def demo_canary_calibration():
    print("--- Canary Calibration Demo ---")
    manager = RollbackPolicyManager()
    manager.deploy({"policy1": "stable_rules"})
    manager.deploy({"policy1": "canary_rules"}) # Deploy canary

    estimator = BayesianEstimator(initial_threshold=0.8, prior_alpha=1, prior_beta=9) # FP rate ~ 0.1
    router = CanaryCalibrationRouter(manager, estimator, max_fp_rate=0.2, canary_fraction=0.5)

    print(f"Initial policy state: {manager.active_policies}")
    print(f"Route 1: {router.route_request('test')}")
    print(f"Route 2: {router.route_request('test')}")

    print("Observing false positives...")
    estimator.observe(True)
    estimator.observe(True)
    estimator.observe(True)
    print(f"New estimated FP rate: {estimator.get_estimated_fp_rate():.2f}")

    print("Routing after high FP rate (expecting auto-rollback):")
    print(f"Route 3: {router.route_request('test')}")
    print(f"Current policy state (should be rolled back): {manager.active_policies}")

if __name__ == "__main__":
    demo_streaming_filter()
    demo_canary_calibration()
