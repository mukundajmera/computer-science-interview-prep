"""
Model adapter module.

Provides an abstract interface for LLM generation and two concrete
stub adapters for testing without real API dependencies.

Design patterns:
    - Strategy — interchangeable model backends behind a uniform interface
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    """Abstract interface for generating LLM output from a prompt.

    Concrete implementations wrap real LLM APIs or provide deterministic
    stubs for testing.
    """

    @abstractmethod
    def generate(self, input_text: str) -> str:
        """Produce model output for the given prompt.

        Args:
            input_text: The prompt string.

        Returns:
            Generated text.
        """


class EchoAdapter(ModelAdapter):
    """Stub adapter that returns the input text unchanged.

    Useful for metric-level testing where the model output must be
    predictable and controllable.
    """

    def generate(self, input_text: str) -> str:
        """Return *input_text* as-is."""
        return input_text


class StaticAdapter(ModelAdapter):
    """Stub adapter that always returns a fixed response.

    Args:
        response: The static string to return for every call.

    Useful for testing metrics against a known output regardless of input.
    """

    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, input_text: str) -> str:
        """Return the pre-configured static response."""
        return self.response
