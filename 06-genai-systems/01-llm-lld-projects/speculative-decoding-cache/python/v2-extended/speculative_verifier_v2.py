"""
Speculative Decoding Verifier - v2-extended.

A deliberate step up from ``v1-basic/speculative_verifier.py``. It keeps the
v1 public API names (``SpeculativeDecodingVerifier`` with
``generate_draft_tokens``, ``calculate_acceptance_probability``,
``verify_step``, ``get_speedup_ratio``, and the ``accepted_tokens_count`` /
``target_evaluations`` / ``kv_cache_length`` attributes) and the exact v1
acceptance-loop semantics, while implementing three improvements the project's
own documents name:

1. **Per-sequence KV-cache isolation** (PROBLEM.md, "Context Isolation"
   limitation). v1 keeps a single global ``kv_cache_length``, so interleaved
   sequences corrupt each other's context accounting. v2 tracks the KV cache
   length per ``sequence_id`` (a new optional ``verify_step`` keyword,
   defaulting to ``"default"`` for full v1 parity), exposes
   ``get_sequence_lengths()``, and adds ``reset_sequence()`` to release a
   finished sequence's context. ``kv_cache_length`` remains as a property on
   the default sequence so single-sequence callers see v1 behavior.

2. **Injectable, seedable randomness.** v1 draws from the global ``random``
   module, so tests must monkeypatch process-wide state. v2 uses an instance
   ``random.Random`` (``__init__(k=4, seed=None)``): seeded verifiers are
   fully reproducible, and no global patching is needed or honored.

3. **Input hardening and acceptance-rate metrics** (PITFALLS 2 operationalized:
   a low acceptance rate means negative speedup, so it must be observable).
   ``verify_step`` validates non-empty drafts, equal-length probability
   vectors, and probabilities within [0, 1] (v1 raised a bare IndexError or
   silently accepted garbage); the constructor validates ``k``. v2 counts
   evaluated vs accepted draft tokens and exposes ``get_acceptance_rate()``
   plus a ``metrics()`` snapshot next to the v1 ``get_speedup_ratio()``.

Standard library only. Python 3.8 compatible. The v1 simulation boundaries
still apply: no real inference, tensors, or VRAM accounting.
"""

import random
from typing import Any, Dict, List, Optional, Tuple


class SpeculativeDecodingVerifier:
    """
    Simulates the speculative-decoding token acceptance loop.

    Time complexity is O(K) per verification step; space is O(K) for the
    accepted list plus O(S) for the per-sequence KV length table.
    """

    def __init__(self, k: int = 4, seed: Optional[int] = None):
        """
        Initializes the verifier.

        Args:
            k: The number of draft tokens generated in one step.
            seed: Optional seed for the instance RNG; when set, draft
                generation and acceptance sampling are fully reproducible.

        Raises:
            ValueError: if k is not a positive integer.
        """
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError("k must be a positive integer.")
        self.k = k
        self.accepted_tokens_count = 0
        self.target_evaluations = 0
        self._rng = random.Random(seed)
        self._sequences: Dict[str, int] = {"default": 0}
        self._draft_tokens_offered = 0
        self._draft_tokens_accepted = 0

    @property
    def kv_cache_length(self) -> int:
        """KV cache length of the default sequence (v1-compatible view). O(1)."""
        return self._sequences.get("default", 0)

    def get_sequence_lengths(self) -> Dict[str, int]:
        """Returns a copy of the per-sequence KV cache lengths. O(S)."""
        return dict(self._sequences)

    def reset_sequence(self, sequence_id: str = "default") -> bool:
        """
        Releases a sequence's KV cache context (e.g., when the request ends).
        Returns True when the sequence existed. O(1).
        """
        if sequence_id in self._sequences:
            del self._sequences[sequence_id]
            return True
        return False

    def generate_draft_tokens(self, vocab_size: int = 32000) -> Tuple[List[int], List[float]]:
        """
        Simulates the generation of K draft tokens along with their
        probabilities, using the instance RNG. O(K).

        Raises:
            ValueError: if vocab_size is not a positive integer.
        """
        if not isinstance(vocab_size, int) or isinstance(vocab_size, bool) or vocab_size <= 0:
            raise ValueError("vocab_size must be a positive integer.")
        tokens = [self._rng.randint(0, vocab_size - 1) for _ in range(self.k)]
        probs = [self._rng.uniform(0.1, 0.9) for _ in range(self.k)]
        return tokens, probs

    def calculate_acceptance_probability(self, p_target: float, p_draft: float) -> float:
        """
        Calculates the acceptance probability for a token:
        min(1, p_target(x) / p_draft(x)). O(1).
        """
        if p_draft == 0.0:
            return 1.0 if p_target > 0.0 else 0.0
        return min(1.0, p_target / p_draft)

    @staticmethod
    def _validate_step_inputs(draft_tokens: List[int], p_draft: List[float],
                              p_target: List[float]) -> None:
        """Fail-fast validation; v1 raised IndexError or accepted garbage."""
        if not draft_tokens:
            raise ValueError("draft_tokens must not be empty.")
        if len(p_draft) != len(draft_tokens) or len(p_target) != len(draft_tokens):
            raise ValueError(
                "p_draft and p_target must have the same length as draft_tokens.")
        for prob in list(p_draft) + list(p_target):
            if prob < 0.0 or prob > 1.0:
                raise ValueError("probabilities must be within [0.0, 1.0].")

    def verify_step(
        self,
        draft_tokens: List[int],
        p_draft: List[float],
        p_target: List[float],
        resample_token_id: int,
        fallback_token_id: int,
        sequence_id: str = "default"
    ) -> Tuple[List[int], int]:
        """
        Simulates the token acceptance/rejection loop for one sequence.

        Same algorithm as v1: accept token i when ``rng <= min(1, pt/pd)``;
        on rejection append ``resample_token_id`` and halt; on full acceptance
        append ``fallback_token_id``. The KV cache length of ``sequence_id``
        grows by the number of emitted tokens; other sequences are untouched.

        Returns:
            Tuple of (accepted_tokens, updated_kv_cache_length for sequence_id)
        """
        self._validate_step_inputs(draft_tokens, p_draft, p_target)

        self.target_evaluations += 1
        accepted = []

        for i in range(len(draft_tokens)):
            pt = p_target[i]
            pd = p_draft[i]
            acc_prob = self.calculate_acceptance_probability(pt, pd)
            self._draft_tokens_offered += 1

            if self._rng.random() <= acc_prob:
                accepted.append(draft_tokens[i])
                self.accepted_tokens_count += 1
                self._draft_tokens_accepted += 1
            else:
                # Rejection triggers a resampling fallback
                accepted.append(resample_token_id)
                self.accepted_tokens_count += 1

                # Prefix reuse length increases by accepted tokens (including resampled)
                new_length = self._sequences.get(sequence_id, 0) + len(accepted)
                self._sequences[sequence_id] = new_length
                return accepted, new_length

        # All K draft tokens accepted: one extra token from the target model
        accepted.append(fallback_token_id)
        self.accepted_tokens_count += 1

        new_length = self._sequences.get(sequence_id, 0) + len(accepted)
        self._sequences[sequence_id] = new_length
        return accepted, new_length

    def get_speedup_ratio(self) -> float:
        """accepted_tokens_count / target_evaluations (v1 formula). O(1)."""
        if self.target_evaluations == 0:
            return 0.0
        return self.accepted_tokens_count / self.target_evaluations

    def get_acceptance_rate(self) -> float:
        """
        Fraction of *evaluated* draft tokens that were accepted (resampled and
        fallback tokens are excluded). A low rate warns of the negative
        speedup scenario in PITFALLS 2. O(1).
        """
        if self._draft_tokens_offered == 0:
            return 0.0
        return self._draft_tokens_accepted / self._draft_tokens_offered

    def metrics(self) -> Dict[str, Any]:
        """Snapshot of counters and ratios for observability. O(S)."""
        return {
            "accepted_tokens_count": self.accepted_tokens_count,
            "target_evaluations": self.target_evaluations,
            "draft_tokens_offered": self._draft_tokens_offered,
            "draft_tokens_accepted": self._draft_tokens_accepted,
            "acceptance_rate": self.get_acceptance_rate(),
            "speedup_ratio": self.get_speedup_ratio(),
            "active_sequences": len(self._sequences),
            "kv_total_length": sum(self._sequences.values()),
        }
