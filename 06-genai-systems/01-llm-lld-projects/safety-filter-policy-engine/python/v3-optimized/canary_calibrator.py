"""
Canary calibration and rollback manager.
"""

from typing import Optional, Dict

class BayesianEstimator:
    """Estimates false-positive rate and updates Bayesian threshold."""

    def __init__(self, initial_threshold: float = 0.5, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        self.threshold = initial_threshold
        self.alpha = prior_alpha
        self.beta = prior_beta

    def observe(self, false_positive: bool) -> None:
        """Update beliefs based on observation (false positive or true positive)."""
        if false_positive:
            self.alpha += 1
        else:
            self.beta += 1

    def get_estimated_fp_rate(self) -> float:
        """Calculate the expected false positive rate."""
        return self.alpha / (self.alpha + self.beta)

    def adjust_threshold(self, target_fp_rate: float) -> float:
        """Adjust the threshold based on the current estimated FP rate."""
        current_fp_rate = self.get_estimated_fp_rate()

        # Simple heuristic: if FP rate is too high, increase the threshold
        if current_fp_rate > target_fp_rate:
            self.threshold = min(0.99, self.threshold + 0.05)
        elif current_fp_rate < target_fp_rate * 0.5:
            self.threshold = max(0.01, self.threshold - 0.05)

        return self.threshold

class RollbackPolicyManager:
    """Manages active policies and rollbacks."""

    def __init__(self):
        self.active_policies: Dict[str, dict] = {}
        self.history: list[Dict[str, dict]] = []

    def deploy(self, policies: Dict[str, dict]) -> None:
        """Deploy new policies, saving the previous state."""
        self.history.append(self.active_policies.copy())
        self.active_policies = policies.copy()

    def rollback(self) -> None:
        """Rollback to the previous policy state."""
        if self.history:
            self.active_policies = self.history.pop()
        else:
            self.active_policies = {}

class CanaryCalibrationRouter:
    """Routes traffic to a canary policy and manages auto-aborts."""

    def __init__(self,
                 manager: RollbackPolicyManager,
                 estimator: BayesianEstimator,
                 max_fp_rate: float = 0.1,
                 canary_fraction: float = 0.1):
        self.manager = manager
        self.estimator = estimator
        self.max_fp_rate = max_fp_rate
        self.canary_fraction = canary_fraction
        self.request_count = 0

    def route_request(self, content: str) -> str:
        """
        Routes the request to either stable or canary.
        Auto-aborts canary if false positive rate exceeds max_fp_rate.
        """
        self.request_count += 1

        # Auto-abort check
        if self.estimator.get_estimated_fp_rate() > self.max_fp_rate:
            self.manager.rollback()
            return "stable" # Return stable since canary was aborted

        if (self.request_count % int(1 / self.canary_fraction)) == 0:
            return "canary"

        return "stable"
