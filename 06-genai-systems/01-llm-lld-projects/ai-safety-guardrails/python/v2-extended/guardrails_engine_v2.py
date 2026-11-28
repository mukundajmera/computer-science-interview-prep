"""
AI Safety Guardrails Engine - v2-extended.

A deliberate step up from ``v1-basic/guardrails_engine.py``. It keeps the v1
public API names (``GuardrailsEngine``, ``GuardrailAction``, ``GuardrailResult``,
``ValidationContext``, ``Guardrail``, ``PreExecutionGuardrail``,
``PostExecutionGuardrail``, ``PIIRedactor``, ``PromptInjectionDetector``,
``ToxicityClassifierStub``, ``HallucinationGroundingChecker`` and the
``validate_input`` / ``validate_output`` signatures) while implementing the
improvements PROBLEM.md's own roadmap assigns to v2-extended:

1. **Async pipeline with parallel post-execution evaluation** (roadmap:
   "async pipeline, parallel execution"; FOLLOW-UPS baseline question 2).
   Guardrails that declare ``is_mutating = False`` (they never REDACT) can run
   concurrently; ``validate_output_async`` evaluates the mutating chain
   sequentially first (REDACT chaining is order-dependent), then runs the
   non-mutating guardrails in parallel via an executor. Among parallel BLOCKs,
   the first in registration order wins, so results stay deterministic.

2. **Custom tenant policies** (roadmap: "custom tenant policies"; FOLLOW-UPS
   variant 3). A ``TenantPolicy`` per tenant can disable named guardrails and
   contribute extra PII regex patterns, applied per request through the
   ``ValidationContext`` rather than mutable guardrail state (PITFALLS 2).

3. **Rejection-rate metrics hooks** (FOLLOW-UPS staff question 2). A
   thread-safe ``GuardrailMetrics`` records per-guardrail evaluations, blocks,
   redacts, and allows, with an optional ``metrics_hook`` callback, so false
   positives can be monitored per guardrail per tenant.

Additionally, guardrails can now be removed by name (v1 only supported add).

Standard library only. Python 3.8 compatible. Simulation/stub boundaries from
v1 are unchanged: no production-grade safety, real tokenization, or embeddings.
"""

import asyncio
import re
import threading
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple


class GuardrailAction(Enum):
    ALLOW = auto()
    BLOCK = auto()
    REDACT = auto()


@dataclass
class ValidationContext:
    tenant_id: str
    source_context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailResult:
    action: GuardrailAction
    text: str
    reason: str


@dataclass
class TenantPolicy:
    """
    Per-tenant guardrail policy.

    disabled_guardrails: guardrail names skipped for this tenant.
    extra_pii_patterns: additional regex strings (name -> pattern) the
        PIIRedactor applies for this tenant only.
    """
    disabled_guardrails: FrozenSet[str] = frozenset()
    extra_pii_patterns: Dict[str, str] = field(default_factory=dict)


class GuardrailMetrics:
    """
    Thread-safe per-guardrail event counters (v2; the v1 baseline deliberately
    avoided threading, but the async executor path requires it).
    """

    ACTIONS = ("evaluations", "allows", "blocks", "redacts")

    def __init__(self) -> None:
        """Initializes empty counters with an internal lock. Complexity: O(1)."""
        self._counts: Dict[str, Dict[str, int]] = {}
        self._lock = threading.Lock()

    def record(self, guardrail_name: str, action: GuardrailAction) -> None:
        """
        Records one evaluation outcome for a guardrail. Complexity: O(1).
        """
        with self._lock:
            entry = self._counts.setdefault(
                guardrail_name, {key: 0 for key in self.ACTIONS}
            )
            entry["evaluations"] += 1
            if action is GuardrailAction.ALLOW:
                entry["allows"] += 1
            elif action is GuardrailAction.BLOCK:
                entry["blocks"] += 1
            elif action is GuardrailAction.REDACT:
                entry["redacts"] += 1

    def snapshot(self) -> Dict[str, Dict[str, int]]:
        """Returns a deep-enough copy of the counters. Complexity: O(G)."""
        with self._lock:
            return {name: dict(entry) for name, entry in self._counts.items()}


class Guardrail:
    """
    Abstract base class for all guardrails.

    ``is_mutating`` declares whether evaluate can return REDACT with modified
    text. Non-mutating guardrails are eligible for parallel execution in the
    async pipeline. Guardrails must stay stateless across requests: all
    request data belongs in the ValidationContext (PITFALLS 2).

    This component enforces strict privacy invariants: explicitly prohibiting
    external provider calls and sensitive prompt logs. It operates as a
    bounded microcomponent with model/provider-independent interfaces.
    Unsupported guarantees: production safety, tokenization, embeddings.
    """

    is_mutating: bool = True

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        raise NotImplementedError


class PreExecutionGuardrail(Guardrail):
    """Base class for pre-execution guardrails."""


class PostExecutionGuardrail(Guardrail):
    """Base class for post-execution guardrails."""


class PIIRedactor(PreExecutionGuardrail):
    """
    Detects and redacts PII based on regex rules, plus any per-tenant
    ``extra_pii_patterns`` supplied through the ValidationContext metadata.

    O(N * P) where N is the input length and P the number of active patterns.
    """

    def __init__(self):
        super().__init__("PIIRedactor")
        self.patterns = {
            "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
            "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
        }

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        patterns = list(self.patterns.items())
        extra = context.metadata.get("extra_pii_patterns", {})
        for category, pattern_str in extra.items():
            try:
                patterns.append((category, re.compile(pattern_str)))
            except re.error as exc:
                raise ValueError(
                    "Invalid extra PII pattern %r: %s" % (category, exc)
                )

        modified_text = text
        found_pii = False

        for category, regex_pattern in patterns:
            if regex_pattern.search(modified_text):
                found_pii = True
                modified_text = regex_pattern.sub(
                    "[%s_REDACTED]" % category.upper(), modified_text
                )

        if found_pii:
            return GuardrailResult(GuardrailAction.REDACT, modified_text,
                                   "PII detected and redacted.")
        return GuardrailResult(GuardrailAction.ALLOW, text, "No PII detected.")


class PromptInjectionDetector(PreExecutionGuardrail):
    """
    Heuristic-based prompt injection detector (non-mutating).
    O(M) where M is the number of heuristic rules evaluated against the input.
    """

    is_mutating = False

    def __init__(self):
        super().__init__("PromptInjectionDetector")
        self.blocklist = [
            "ignore previous instructions",
            "system prompt",
            "you are now a",
            "canary_token_123"
        ]

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        text_lower = text.lower()
        for heuristic in self.blocklist:
            if heuristic in text_lower:
                return GuardrailResult(GuardrailAction.BLOCK, "",
                                       "Prompt injection detected")
        return GuardrailResult(GuardrailAction.ALLOW, text,
                               "No prompt injection detected.")


class ToxicityClassifierStub(PostExecutionGuardrail):
    """
    Stub for toxicity classification (non-mutating).
    O(1) time complexity for this stub implementation.
    """

    is_mutating = False

    def __init__(self, threshold: float = 0.5):
        super().__init__("ToxicityClassifierStub")
        self.threshold = threshold
        self.toxic_keywords = ["toxic", "hate", "abuse"]

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        text_lower = text.lower()
        for keyword in self.toxic_keywords:
            if keyword in text_lower:
                return GuardrailResult(GuardrailAction.BLOCK, "",
                                       "Toxicity detected.")
        return GuardrailResult(GuardrailAction.ALLOW, text,
                               "No toxicity detected.")


class HallucinationGroundingChecker(PostExecutionGuardrail):
    """
    Checks if output claims are grounded in source context (non-mutating).
    O(N*M) worst-case stub, checking generated claims against source tokens.
    """

    is_mutating = False

    def __init__(self):
        super().__init__("HallucinationGroundingChecker")

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        text_lower = text.lower()
        if "unsupported_claim" in text_lower:
            return GuardrailResult(GuardrailAction.BLOCK, "",
                                   "Hallucination detected.")
        return GuardrailResult(GuardrailAction.ALLOW, text,
                               "Content appears grounded.")


class GuardrailsEngine:
    """
    Orchestrates pre and post-execution guardrails, sync and async.

    Sequential semantics (v1) are preserved exactly: fast-fail on BLOCK,
    REDACT updates the working text, and the mutating chain always runs in
    registration order before any parallel non-mutating evaluation.

    Overall complexity is the sum of O(N) evaluations for active guardrails;
    the async path overlaps non-mutating evaluations on an executor.
    """

    def __init__(self, policies: Optional[Dict[str, TenantPolicy]] = None,
                 metrics_hook: Optional[Callable[[str, str, str], None]] = None) -> None:
        """
        Initializes the engine.

        policies maps tenant_id to TenantPolicy; tenants without an entry get
        the default policy (everything enabled, no extra patterns).
        metrics_hook, when set, is called as
        ``hook(guardrail_name, action_name, tenant_id)`` per evaluation.
        """
        self.pre_guardrails: List[PreExecutionGuardrail] = []
        self.post_guardrails: List[PostExecutionGuardrail] = []
        self._policies: Dict[str, TenantPolicy] = dict(policies or {})
        self.metrics = GuardrailMetrics()
        self._metrics_hook = metrics_hook

    def add_pre_guardrail(self, guardrail: PreExecutionGuardrail) -> None:
        """Registers a pre-execution guardrail. Complexity: O(1)."""
        self.pre_guardrails.append(guardrail)

    def add_post_guardrail(self, guardrail: PostExecutionGuardrail) -> None:
        """Registers a post-execution guardrail. Complexity: O(1)."""
        self.post_guardrails.append(guardrail)

    def remove_pre_guardrail(self, name: str) -> bool:
        """
        Removes the first pre-execution guardrail with the given name.

        Returns True when one was removed. Complexity: O(G).
        """
        return self._remove_from(self.pre_guardrails, name)

    def remove_post_guardrail(self, name: str) -> bool:
        """
        Removes the first post-execution guardrail with the given name.

        Returns True when one was removed. Complexity: O(G).
        """
        return self._remove_from(self.post_guardrails, name)

    @staticmethod
    def _remove_from(guardrails: List[Guardrail], name: str) -> bool:
        for index, guardrail in enumerate(guardrails):
            if guardrail.name == name:
                del guardrails[index]
                return True
        return False

    def _policy_for(self, context: ValidationContext) -> Optional[TenantPolicy]:
        """Returns the tenant's policy, or None for the default. O(1)."""
        return self._policies.get(context.tenant_id)

    @staticmethod
    def _active(guardrails: List[Guardrail], policy: Optional[TenantPolicy]) -> List[Guardrail]:
        """Filters out guardrails disabled by the tenant policy. O(G)."""
        if policy is None or not policy.disabled_guardrails:
            return list(guardrails)
        return [g for g in guardrails if g.name not in policy.disabled_guardrails]

    @staticmethod
    def _context_with_policy(context: ValidationContext,
                             policy: Optional[TenantPolicy]) -> ValidationContext:
        """
        Returns a per-call context carrying the policy's extra PII patterns,
        leaving the caller's context object untouched.
        """
        if policy is None or not policy.extra_pii_patterns:
            return context
        merged_metadata = dict(context.metadata)
        merged_metadata["extra_pii_patterns"] = dict(policy.extra_pii_patterns)
        return replace(context, metadata=merged_metadata)

    def _record(self, guardrail: Guardrail, action: GuardrailAction, tenant_id: str) -> None:
        """Records metrics and invokes the optional hook."""
        self.metrics.record(guardrail.name, action)
        if self._metrics_hook is not None:
            self._metrics_hook(guardrail.name, action.name, tenant_id)

    def _run_sequential(self, guardrails: List[Guardrail], text: str,
                        context: ValidationContext, pass_reason: str) -> GuardrailResult:
        """The v1 chain: fast-fail on BLOCK, thread REDACT text through."""
        current_text = text
        final_action = GuardrailAction.ALLOW
        for guardrail in guardrails:
            result = guardrail.evaluate(current_text, context)
            self._record(guardrail, result.action, context.tenant_id)
            if result.action == GuardrailAction.BLOCK:
                return result
            elif result.action == GuardrailAction.REDACT:
                final_action = GuardrailAction.REDACT
                current_text = result.text
        return GuardrailResult(final_action, current_text, pass_reason)

    def validate_input(self, text: str, context: ValidationContext) -> GuardrailResult:
        """
        Validates input against all active pre-execution guardrails.

        Time complexity: Sum of all active pre-guardrail evaluations.
        """
        if not text:
            return GuardrailResult(GuardrailAction.BLOCK, "",
                                   "Empty input provided.")
        policy = self._policy_for(context)
        context = self._context_with_policy(context, policy)
        return self._run_sequential(self._active(self.pre_guardrails, policy),
                                    text, context, "Input validation passed.")

    def validate_output(self, text: str, context: ValidationContext) -> GuardrailResult:
        """
        Validates output against all active post-execution guardrails.

        Time complexity: Sum of all active post-guardrail evaluations.
        """
        policy = self._policy_for(context)
        context = self._context_with_policy(context, policy)
        return self._run_sequential(self._active(self.post_guardrails, policy),
                                    text, context, "Output validation passed.")

    async def validate_input_async(self, text: str,
                                   context: ValidationContext) -> GuardrailResult:
        """
        Async input validation. Pre-execution guardrails chain REDACTs, so the
        phase stays sequential by design; the async signature lets callers
        compose it with validate_output_async.
        """
        return self.validate_input(text, context)

    async def validate_output_async(self, text: str,
                                    context: ValidationContext) -> GuardrailResult:
        """
        Async output validation: mutating guardrails run sequentially first
        (REDACT chaining is order-dependent), then all non-mutating guardrails
        run concurrently on the final text via the default executor.

        Among concurrent BLOCKs, the first in registration order wins, so the
        outcome is deterministic for a fixed configuration.

        Time complexity: O(max(non-mutating evaluations)) after the mutating
        chain, instead of O(sum).
        """
        policy = self._policy_for(context)
        context = self._context_with_policy(context, policy)
        active = self._active(self.post_guardrails, policy)

        mutating = [g for g in active if g.is_mutating]
        non_mutating = [g for g in active if not g.is_mutating]

        chain_result = self._run_sequential(mutating, text, context,
                                            "Output validation passed.")
        if chain_result.action == GuardrailAction.BLOCK:
            return chain_result

        current_text = chain_result.text
        final_action = chain_result.action

        if non_mutating:
            loop = asyncio.get_running_loop()
            results = await asyncio.gather(*[
                loop.run_in_executor(None, g.evaluate, current_text, context)
                for g in non_mutating
            ])
            for guardrail, result in zip(non_mutating, results):
                self._record(guardrail, result.action, context.tenant_id)
            for result in results:
                if result.action == GuardrailAction.BLOCK:
                    return result

        return GuardrailResult(final_action, current_text,
                               "Output validation passed.")

    def metrics_snapshot(self) -> Dict[str, Dict[str, int]]:
        """Returns per-guardrail evaluation counters. Complexity: O(G)."""
        return self.metrics.snapshot()
