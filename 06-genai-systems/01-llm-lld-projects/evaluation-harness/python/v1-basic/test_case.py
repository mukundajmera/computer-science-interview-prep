"""
Test case and test suite module.

Provides dataclasses for defining evaluation test cases and a suite
container with tag-based filtering support.

Design patterns:
    - None (pure data carriers and collection management)
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TestCase:
    """A single evaluation example with input, expected output, and metadata.

    Attributes:
        case_id:         Unique identifier, auto-generated UUID.
        input_text:      Prompt to send to the model.
        expected_output: Ground-truth answer for scoring.
        tags:            Category labels for filtering (e.g. ``["summarisation"]``).
        metadata:        Arbitrary key-value pairs for extra context.
    """

    input_text: str
    expected_output: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    case_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class TestSuite:
    """Named collection of :class:`TestCase` instances with filtering.

    Args:
        name: Human-readable suite identifier.

    Attributes:
        name:       Suite identifier.
        test_cases: Ordered list of test cases.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.test_cases: List[TestCase] = []

    def add_case(self, case: TestCase) -> None:
        """Append a test case to the suite.

        Args:
            case: The :class:`TestCase` to add.
        """
        self.test_cases.append(case)

    def filter_by_tag(self, tag: str) -> List[TestCase]:
        """Return test cases that contain the given tag.

        Args:
            tag: Tag string to filter on (exact match).

        Returns:
            List of matching :class:`TestCase` instances.
        """
        return [tc for tc in self.test_cases if tag in tc.tags]

    def size(self) -> int:
        """Return the number of test cases in the suite."""
        return len(self.test_cases)
