import os
import sys
from unittest.mock import patch

import pytest

# Adjust sys.path to load the v2 module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
from speculative_verifier_v2 import SpeculativeDecodingVerifier


class StubRng:
    """Deterministic stand-in for random.Random: pops scripted uniform draws."""

    def __init__(self, values):
        self._values = list(values)

    def random(self):
        if len(self._values) > 1:
            return self._values.pop(0)
        return self._values[0]


def stubbed_verifier(k, draws):
    verifier = SpeculativeDecodingVerifier(k=k)
    verifier._rng = StubRng(draws)
    return verifier


# --- v1 fixture parity (names, counters, and default-sequence behavior kept) ---

def test_exact_match_full_acceptance():
    verifier = stubbed_verifier(k=3, draws=[0.99])
    accepted, kv_len = verifier.verify_step(
        draft_tokens=[10, 20, 30], p_draft=[0.1, 0.2, 0.3],
        p_target=[0.2, 0.3, 0.4], resample_token_id=99, fallback_token_id=100)
    assert accepted == [10, 20, 30, 100]
    assert kv_len == 4
    assert verifier.accepted_tokens_count == 4
    assert verifier.target_evaluations == 1


def test_partial_rejection_and_resample():
    verifier = stubbed_verifier(k=3, draws=[0.5, 0.5])  # 0.5 > 0.25 rejects token 20
    accepted, kv_len = verifier.verify_step(
        draft_tokens=[10, 20, 30], p_draft=[0.5, 0.8, 0.5],
        p_target=[0.5, 0.2, 0.5], resample_token_id=99, fallback_token_id=100)
    assert accepted == [10, 99]
    assert kv_len == 2
    assert verifier.accepted_tokens_count == 2
    assert verifier.target_evaluations == 1


def test_speedup_calculation():
    verifier = stubbed_verifier(k=2, draws=[0.99])
    verifier.verify_step([10, 20], [0.1, 0.1], [0.2, 0.2], 99, 100)
    verifier._rng = StubRng([0.5])  # 0.5 > 0.125 rejects first token
    verifier.verify_step([30, 40], [0.8, 0.1], [0.1, 0.1], 99, 100)
    assert verifier.target_evaluations == 2
    assert verifier.accepted_tokens_count == 4
    assert verifier.get_speedup_ratio() == 2.0


def test_kv_cache_prefix_reuse_default_sequence():
    verifier = stubbed_verifier(k=3, draws=[0.99])
    assert verifier.kv_cache_length == 0
    verifier.verify_step([1, 2, 3], [0.1] * 3, [0.2] * 3, 99, 100)
    assert verifier.kv_cache_length == 4
    verifier._rng = StubRng([0.05, 0.5])
    verifier.verify_step([4, 5, 6], [0.1, 0.9, 0.1], [0.2, 0.1, 0.2], 99, 100)
    assert verifier.kv_cache_length == 6


def test_acceptance_probability_edge_parity():
    verifier = SpeculativeDecodingVerifier()
    assert verifier.calculate_acceptance_probability(0.5, 0.0) == 1.0
    assert verifier.calculate_acceptance_probability(0.0, 0.0) == 0.0
    assert verifier.calculate_acceptance_probability(0.9, 0.1) == 1.0
    assert verifier.calculate_acceptance_probability(0.1, 0.4) == 0.25


# --- v2: seedable instance RNG ---

def test_seeded_rng_reproducible():
    first = SpeculativeDecodingVerifier(k=4, seed=42)
    second = SpeculativeDecodingVerifier(k=4, seed=42)
    assert first.generate_draft_tokens() == second.generate_draft_tokens()
    different = SpeculativeDecodingVerifier(k=4, seed=7)
    assert first.generate_draft_tokens() != different.generate_draft_tokens()


def test_no_global_random_dependency():
    verifier = SpeculativeDecodingVerifier(k=3, seed=1)
    # Patching the module-level random must not (and need not) affect v2.
    with patch('random.random', side_effect=AssertionError("global random used")):
        verifier.generate_draft_tokens(vocab_size=100)
        accepted, _ = verifier.verify_step(
            [1, 2, 3], [0.1, 0.1, 0.1], [0.2, 0.2, 0.2], 99, 100)
    assert len(accepted) == 4


# --- v2: per-sequence KV-cache isolation ---

def test_per_sequence_kv_isolation():
    verifier = stubbed_verifier(k=2, draws=[0.99])
    _, kv_a = verifier.verify_step([1, 2], [0.1, 0.1], [0.2, 0.2], 99, 100,
                                   sequence_id="seq-a")
    _, kv_b = verifier.verify_step([3], [0.1], [0.2], 99, 100,
                                   sequence_id="seq-b")
    assert kv_a == 3  # 2 drafts + fallback
    assert kv_b == 2  # 1 draft + fallback; independent of seq-a
    # The default sequence exists from construction with length 0.
    assert verifier.get_sequence_lengths() == {"default": 0, "seq-a": 3, "seq-b": 2}
    # The v1-compatible property only reflects the default sequence.
    assert verifier.kv_cache_length == 0


def test_reset_sequence_releases_context():
    verifier = stubbed_verifier(k=2, draws=[0.99])
    verifier.verify_step([1, 2], [0.1, 0.1], [0.2, 0.2], 99, 100, sequence_id="seq-a")
    assert verifier.reset_sequence("seq-a") is True
    assert verifier.reset_sequence("seq-a") is False
    assert "seq-a" not in verifier.get_sequence_lengths()


# --- v2: acceptance-rate metrics ---

def test_acceptance_rate_counts_only_evaluated_drafts():
    verifier = stubbed_verifier(k=4, draws=[0.99, 0.5])
    # Token 1 accepted (0.99 <= 1.0), token 2 rejected (0.5 > 0.25);
    # tokens 3 and 4 are discarded without evaluation.
    verifier.verify_step([10, 20, 30, 40], [0.5, 0.8, 0.5, 0.5],
                         [0.5, 0.2, 0.5, 0.5], 99, 100)
    assert verifier.metrics()["draft_tokens_offered"] == 2
    assert verifier.metrics()["draft_tokens_accepted"] == 1
    assert verifier.get_acceptance_rate() == 0.5


def test_metrics_snapshot_fields():
    verifier = stubbed_verifier(k=2, draws=[0.99])
    verifier.verify_step([1, 2], [0.1, 0.1], [0.2, 0.2], 99, 100, sequence_id="s1")
    snapshot = verifier.metrics()
    assert snapshot["accepted_tokens_count"] == 3
    assert snapshot["target_evaluations"] == 1
    assert snapshot["acceptance_rate"] == 1.0
    assert snapshot["speedup_ratio"] == 3.0
    assert snapshot["active_sequences"] == 2  # default + s1
    assert snapshot["kv_total_length"] == 3
    assert SpeculativeDecodingVerifier().get_acceptance_rate() == 0.0


# --- v2: input hardening ---

def test_verify_step_input_validation():
    verifier = SpeculativeDecodingVerifier(k=3)
    with pytest.raises(ValueError, match="must not be empty"):
        verifier.verify_step([], [], [], 99, 100)
    with pytest.raises(ValueError, match="same length"):
        verifier.verify_step([1, 2], [0.1], [0.1, 0.1], 99, 100)
    with pytest.raises(ValueError, match="same length"):
        verifier.verify_step([1, 2], [0.1, 0.1], [0.1], 99, 100)
    with pytest.raises(ValueError, match=r"within \[0.0, 1.0\]"):
        verifier.verify_step([1], [1.5], [0.5], 99, 100)
    with pytest.raises(ValueError, match=r"within \[0.0, 1.0\]"):
        verifier.verify_step([1], [0.5], [-0.1], 99, 100)
    # Validation happens before any counter changes.
    assert verifier.target_evaluations == 0
    assert verifier.accepted_tokens_count == 0


def test_constructor_and_vocab_validation():
    with pytest.raises(ValueError, match="k must be a positive integer"):
        SpeculativeDecodingVerifier(k=0)
    with pytest.raises(ValueError, match="k must be a positive integer"):
        SpeculativeDecodingVerifier(k=-2)
    verifier = SpeculativeDecodingVerifier(k=1)
    with pytest.raises(ValueError, match="vocab_size must be a positive integer"):
        verifier.generate_draft_tokens(vocab_size=0)
