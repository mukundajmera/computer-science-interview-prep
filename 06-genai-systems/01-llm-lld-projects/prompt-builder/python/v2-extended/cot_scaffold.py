"""
Chain-of-Thought (CoT) scaffold template builder.
"""
from typing import List

class CoTScaffold:
    """
    Constructs Chain-of-Thought prompts with clear reasoning steps.
    """
    def __init__(self, steps: List[str] = None):
        if steps is None:
            self.steps = [
                "Understand the core problem.",
                "Identify edge cases or constraints.",
                "Formulate a step-by-step plan.",
                "Execute the plan.",
                "Review the final result against the original problem."
            ]
        else:
            self.steps = steps

    def build_scaffold(self) -> str:
        """
        Builds the CoT scaffold string.
        """
        lines = ["Let's think step by step:"]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("\nPlease output your thought process before providing the final answer.")
        return "\n".join(lines)
