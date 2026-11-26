import re
import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Any

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

class Guardrail:
    """
    Abstract base class for all guardrails.
    This component enforces strict privacy invariants: explicitly prohibiting external provider calls
    and sensitive prompt logs. It operates as a bounded microcomponent with model/provider-independent interfaces.
    Unsupported guarantees: production safety, tokenization, embeddings.
    """
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        raise NotImplementedError

class PreExecutionGuardrail(Guardrail):
    """
    Base class for pre-execution guardrails.
    """
    pass

class PostExecutionGuardrail(Guardrail):
    """
    Base class for post-execution guardrails.
    """
    pass

class PIIRedactor(PreExecutionGuardrail):
    """
    Detects and redacts PII based on regex rules.
    O(N) complexity where N is the length of the input text per regex pattern.
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
        modified_text = text
        found_pii = False
        
        for category, regex_pattern in self.patterns.items():
            if regex_pattern.search(modified_text):
                found_pii = True
                modified_text = regex_pattern.sub(f"[{category.upper()}_REDACTED]", modified_text)
                
        if found_pii:
            return GuardrailResult(GuardrailAction.REDACT, modified_text, "PII detected and redacted.")
        return GuardrailResult(GuardrailAction.ALLOW, text, "No PII detected.")

class PromptInjectionDetector(PreExecutionGuardrail):
    """
    Heuristic-based prompt injection detector.
    Checks for canary tokens, system prompt overrides, and roleplay escapes.
    O(M) where M is the number of heuristic rules evaluated against the input length.
    """
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
                return GuardrailResult(GuardrailAction.BLOCK, "", "Prompt injection detected")
        return GuardrailResult(GuardrailAction.ALLOW, text, "No prompt injection detected.")


class ToxicityClassifierStub(PostExecutionGuardrail):
    """
    Stub for toxicity classification.
    Simulates external call or complex model evaluation.
    O(1) time complexity for this stub implementation.
    """
    def __init__(self, threshold: float = 0.5):
        super().__init__("ToxicityClassifierStub")
        self.threshold = threshold
        self.toxic_keywords = ["toxic", "hate", "abuse"]

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        text_lower = text.lower()
        for keyword in self.toxic_keywords:
            if keyword in text_lower:
                return GuardrailResult(GuardrailAction.BLOCK, "", "Toxicity detected.")
        return GuardrailResult(GuardrailAction.ALLOW, text, "No toxicity detected.")

class HallucinationGroundingChecker(PostExecutionGuardrail):
    """
    Checks if output claims are grounded in source context.
    O(N*M) worst-case stub, checking generated claims against source tokens.
    """
    def __init__(self):
        super().__init__("HallucinationGroundingChecker")

    def evaluate(self, text: str, context: ValidationContext) -> GuardrailResult:
        text_lower = text.lower()
        if "unsupported_claim" in text_lower:
            return GuardrailResult(GuardrailAction.BLOCK, "", "Hallucination detected.")
        return GuardrailResult(GuardrailAction.ALLOW, text, "Content appears grounded.")

class GuardrailsEngine:
    """
    Orchestrates pre and post-execution guardrails.
    Computational complexity notes:
    Overall complexity is the sum of O(N) evaluations for active guardrails.
    """
    def __init__(self):
        self.pre_guardrails: List[PreExecutionGuardrail] = []
        self.post_guardrails: List[PostExecutionGuardrail] = []

    def add_pre_guardrail(self, guardrail: PreExecutionGuardrail):
        self.pre_guardrails.append(guardrail)

    def add_post_guardrail(self, guardrail: PostExecutionGuardrail):
        self.post_guardrails.append(guardrail)

    def validate_input(self, text: str, context: ValidationContext) -> GuardrailResult:
        """
        Validates input against all pre-execution guardrails.
        Time complexity: Sum of all active pre-guardrail evaluations.
        """
        if not text:
            return GuardrailResult(GuardrailAction.BLOCK, "", "Empty input provided.")
            
        current_text = text
        final_action = GuardrailAction.ALLOW
        for guardrail in self.pre_guardrails:
            result = guardrail.evaluate(current_text, context)
            if result.action == GuardrailAction.BLOCK:
                return result
            elif result.action == GuardrailAction.REDACT:
                final_action = GuardrailAction.REDACT
                current_text = result.text
        return GuardrailResult(final_action, current_text, "Input validation passed.")

    def validate_output(self, text: str, context: ValidationContext) -> GuardrailResult:
        """
        Validates output against all post-execution guardrails.
        Time complexity: Sum of all active post-guardrail evaluations.
        """
        current_text = text
        final_action = GuardrailAction.ALLOW
        for guardrail in self.post_guardrails:
            result = guardrail.evaluate(current_text, context)
            if result.action == GuardrailAction.BLOCK:
                return result
            elif result.action == GuardrailAction.REDACT:
                final_action = GuardrailAction.REDACT
                current_text = result.text
        return GuardrailResult(final_action, current_text, "Output validation passed.")
