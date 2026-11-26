"""
Builder-pattern prompt assembler with budget enforcement.

Provides :class:`PromptBuilder` which collects prompt sections (system
instructions, user messages, context snippets, tool outputs) and assembles
them into a single prompt string.  When the total estimated token count
exceeds the configured budget, lower-priority sections are truncated
automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Dict

from budget import TokenBudget

# Default priority levels (lower number = higher priority = truncated last)
PRIORITY_SYSTEM: int = 0
PRIORITY_USER: int = 0
PRIORITY_TOOLS: int = 1
PRIORITY_CONTEXT: int = 2


@dataclass
class PromptSection:
    """A single content block in an assembled prompt.

    Attributes:
        name:        Section identifier (e.g. ``"system"``).
        content:     Rendered text content.
        priority:    Truncation order — 0 is highest priority (never
                     truncated); higher values are truncated first.
        token_count: Estimated tokens for *content*.
    """

    name: str
    content: str
    priority: int = 0
    token_count: int = 0


class PromptBuilder:
    """Fluent builder for assembling LLM prompts with budget guarding.

    Typical usage::

        prompt = (
            PromptBuilder(max_tokens=4096)
            .set_system_instruction("You are a helpful assistant.")
            .add_context_snippet("Relevant doc paragraph 1 ...")
            .add_context_snippet("Relevant doc paragraph 2 ...")
            .add_tool_output("lint: 0 errors")
            .set_user_message("Fix the warnings.")
            .build()
        )

    Sections are ordered in the final prompt as:
    ``system → context → tools → user``.

    When total estimated tokens exceed the budget, sections are truncated
    starting from the highest priority number (lowest importance).
    """

    SECTION_ORDER: List[str] = ["system", "context", "tools", "user"]

    def __init__(
        self,
        max_tokens: int = 4096,
        *,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        """Initialise the builder.

        Args:
            max_tokens:      Total context-length budget.
            token_estimator: Optional custom token estimator.
        """
        self._budget: TokenBudget = TokenBudget(
            max_tokens=max_tokens,
            token_estimator=token_estimator,
        )
        self._system: Optional[str] = None
        self._user: Optional[str] = None
        self._context_snippets: List[str] = []
        self._tool_outputs: List[str] = []

    # ------------------------------------------------------------------
    # Fluent setters
    # ------------------------------------------------------------------

    def set_system_instruction(self, text: str) -> "PromptBuilder":
        """Set the system instruction section.

        Args:
            text: System instruction content.

        Returns:
            ``self`` for fluent chaining.
        """
        self._system = text
        return self

    def set_user_message(self, text: str) -> "PromptBuilder":
        """Set the user message section.

        Args:
            text: User message content.

        Returns:
            ``self`` for fluent chaining.
        """
        self._user = text
        return self

    def add_context_snippet(self, text: str) -> "PromptBuilder":
        """Append a retrieved context snippet.

        Args:
            text: Context snippet content.

        Returns:
            ``self`` for fluent chaining.
        """
        if text and text.strip():
            self._context_snippets.append(text)
        return self

    def add_tool_output(self, text: str) -> "PromptBuilder":
        """Append a tool output result.

        Args:
            text: Tool output content.

        Returns:
            ``self`` for fluent chaining.
        """
        if text and text.strip():
            self._tool_outputs.append(text)
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> str:
        """Assemble all sections into a final prompt string.

        Applies priority-based truncation when the total estimated tokens
        exceed the configured budget.

        Returns:
            The assembled prompt as a single string.

        Raises:
            ValueError: If no content has been added to the builder.
        """
        sections = self._assemble_sections()
        if not sections:
            raise ValueError("Cannot build an empty prompt")

        sections = self._enforce_budget(sections)
        return self._render(sections)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assemble_sections(self) -> List[PromptSection]:
        """Create PromptSection objects from the accumulated content."""
        sections: List[PromptSection] = []

        if self._system:
            tokens = self._budget.estimate_tokens(self._system)
            sections.append(PromptSection(
                name="system",
                content=self._system,
                priority=PRIORITY_SYSTEM,
                token_count=tokens,
            ))

        if self._context_snippets:
            combined = "\n\n".join(self._context_snippets)
            tokens = self._budget.estimate_tokens(combined)
            sections.append(PromptSection(
                name="context",
                content=combined,
                priority=PRIORITY_CONTEXT,
                token_count=tokens,
            ))

        if self._tool_outputs:
            combined = "\n".join(self._tool_outputs)
            tokens = self._budget.estimate_tokens(combined)
            sections.append(PromptSection(
                name="tools",
                content=combined,
                priority=PRIORITY_TOOLS,
                token_count=tokens,
            ))

        if self._user:
            tokens = self._budget.estimate_tokens(self._user)
            sections.append(PromptSection(
                name="user",
                content=self._user,
                priority=PRIORITY_USER,
                token_count=tokens,
            ))

        return sections

    def _enforce_budget(
        self, sections: List[PromptSection]
    ) -> List[PromptSection]:
        """Truncate lower-priority sections until total fits the budget.

        Sections are processed from highest priority number (least
        important) to lowest.  Priority-0 sections are never truncated.
        """
        total = sum(s.token_count for s in sections)
        if total <= self._budget.max_tokens:
            return sections

        # Sort by priority descending (highest number first = truncate first)
        by_priority = sorted(sections, key=lambda s: s.priority, reverse=True)

        for section in by_priority:
            if total <= self._budget.max_tokens:
                break
            if section.priority == 0:
                # Never truncate priority-0 sections
                continue

            overshoot = total - self._budget.max_tokens
            target_tokens = max(0, section.token_count - overshoot)
            truncated = self._budget.truncate_to_fit(
                section.content, target_tokens
            )
            new_tokens = self._budget.estimate_tokens(truncated)
            total = total - section.token_count + new_tokens
            section.content = truncated
            section.token_count = new_tokens

        if total > self._budget.max_tokens:
            raise ValueError(
                f"Prompt exceeds budget ({total} > {self._budget.max_tokens}) "
                f"even after truncating all non-essential sections. "
                f"Reduce priority-0 content or increase max_tokens."
            )

        return sections

    @staticmethod
    def _render(sections: List[PromptSection]) -> str:
        """Join sections into the final prompt string.

        Sections are ordered according to :attr:`SECTION_ORDER`.
        """
        order_map = {
            name: idx for idx, name in enumerate(PromptBuilder.SECTION_ORDER)
        }
        ordered = sorted(
            sections,
            key=lambda s: order_map.get(s.name, len(order_map)),
        )

        parts: List[str] = []
        for section in ordered:
            if section.content.strip():
                parts.append(section.content)
        return "\n\n".join(parts)

@dataclass
class ChatMessage:
    role: str
    content: str
    priority: int = 0
    token_count: int = 0

class ChatPromptBuilder:
    """
    Builder for assembling dynamic system/user/assistant chat messages with budget enforcement.
    """
    def __init__(
        self,
        max_tokens: int = 4096,
        *,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        self._budget: TokenBudget = TokenBudget(
            max_tokens=max_tokens,
            token_estimator=token_estimator,
        )
        self._messages: List[ChatMessage] = []
        self._system_priority = 0

    def add_message(self, role: str, content: str, priority: int = 1) -> "ChatPromptBuilder":
        if content and content.strip():
            tokens = self._budget.estimate_tokens(content)
            self._messages.append(ChatMessage(role=role, content=content, priority=priority, token_count=tokens))
        return self

    def set_system_message(self, content: str) -> "ChatPromptBuilder":
        # Usually system message is highest priority (0)
        return self.add_message("system", content, priority=0)

    def add_user_message(self, content: str, priority: int = 0) -> "ChatPromptBuilder":
        return self.add_message("user", content, priority=priority)

    def add_assistant_message(self, content: str, priority: int = 2) -> "ChatPromptBuilder":
        return self.add_message("assistant", content, priority=priority)

    def build(self) -> List[Dict[str, str]]:
        if not self._messages:
            raise ValueError("Cannot build an empty prompt")

        import copy
        messages_copy = copy.deepcopy(self._messages)
        # Sort messages by priority descending (highest number = lowest priority = truncate first)
        by_priority = sorted(messages_copy, key=lambda m: m.priority, reverse=True)

        total = sum(m.token_count for m in self._messages)
        
        for message in by_priority:
            if total <= self._budget.max_tokens:
                break
            if message.priority == 0:
                continue

            overshoot = total - self._budget.max_tokens
            target_tokens = max(0, message.token_count - overshoot)
            
            truncated = self._budget.truncate_to_fit(message.content, target_tokens)
            new_tokens = self._budget.estimate_tokens(truncated)
            
            total = total - message.token_count + new_tokens
            message.content = truncated
            message.token_count = new_tokens

        if total > self._budget.max_tokens:
            raise ValueError(
                f"Prompt exceeds budget ({total} > {self._budget.max_tokens}) "
                f"even after truncating all non-essential messages. "
                f"Reduce priority-0 content or increase max_tokens."
            )

        # Remove empty messages after truncation and keep the original order
        final_messages = []
        for msg in messages_copy:
            if msg.content.strip():
                final_messages.append({"role": msg.role, "content": msg.content})
        
        return final_messages
