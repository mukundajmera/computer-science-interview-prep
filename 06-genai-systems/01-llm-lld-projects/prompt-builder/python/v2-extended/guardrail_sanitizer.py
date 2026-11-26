"""
Prompt guardrail sanitization to handle jailbreak prompt detection and XML tag wrapping.
"""
import re

class GuardrailSanitizer:
    """
    Sanitizes user input to prevent prompt injection and jailbreak attacks.
    """

    # Common jailbreak phrases
    JAILBREAK_PATTERNS = [
        re.compile(r"ignore previous instructions", re.IGNORECASE),
        re.compile(r"you are now an unconstrained", re.IGNORECASE),
        re.compile(r"system prompt:", re.IGNORECASE),
        re.compile(r"new instructions:", re.IGNORECASE),
        re.compile(r"do anything now", re.IGNORECASE),
    ]

    @classmethod
    def contains_jailbreak(cls, text: str) -> bool:
        """
        Checks if the text contains known jailbreak patterns.
        """
        for pattern in cls.JAILBREAK_PATTERNS:
            if pattern.search(text):
                return True
        return False

    @classmethod
    def sanitize(cls, text: str) -> str:
        """
        Sanitize user input by wrapping it in an explicit block or XML tags,
        and optionally scrubbing known patterns.
        If a jailbreak pattern is found, we replace it or block the input entirely.
        For simplicity, we'll replace matches with '[REDACTED]'.
        """
        sanitized_text = text
        for pattern in cls.JAILBREAK_PATTERNS:
            sanitized_text = pattern.sub("[REDACTED]", sanitized_text)

        return sanitized_text

    @classmethod
    def wrap_with_tags(cls, text: str, tag_name: str = "user_input") -> str:
        """
        Wraps text in XML tags to demarcate instructions from data.
        """
        return f"<{tag_name}>\n{text}\n</{tag_name}>"
