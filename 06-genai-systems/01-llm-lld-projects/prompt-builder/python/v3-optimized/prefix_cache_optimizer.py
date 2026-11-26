from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PromptSection:
    name: str
    content: str
    is_static: bool = False
    priority: int = 0
    token_count: int = 0

class PrefixCacheOptimizer:
    """Optimizes prompt section ordering to maximize KV-cache reuse.

    Static sections (like system prompts and static few-shot examples)
    should be placed at the very beginning of the prompt in a stable order.
    Dynamic sections (like user queries or varying context) should follow.
    """

    @staticmethod
    def optimize_order(sections: List[PromptSection]) -> List[PromptSection]:
        """
        Reorders sections to maximize prefix caching.

        Rules:
        1. Static sections go first, ordered by priority (lower number = higher priority).
        2. Dynamic sections go next, ordered by priority.
        3. Within the same priority and static-ness, stable alphabetic order by name
           maintains consistency across requests.
        """
        # Separate into static and dynamic
        static_sections = [s for s in sections if s.is_static]
        dynamic_sections = [s for s in sections if not s.is_static]

        # Sort each group: first by priority (ascending), then by name (ascending) for stability
        static_sections.sort(key=lambda s: (s.priority, s.name))
        dynamic_sections.sort(key=lambda s: (s.priority, s.name))

        # Static first, dynamic next
        return static_sections + dynamic_sections

    @staticmethod
    def get_cacheable_prefix(sections: List[PromptSection]) -> str:
        """Returns the concatenated static prefix for logging or debugging."""
        optimized = PrefixCacheOptimizer.optimize_order(sections)
        static_contents = [s.content for s in optimized if s.is_static]
        return "\n\n".join(static_contents)
