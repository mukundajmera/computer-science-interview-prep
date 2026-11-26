import re
from typing import Dict, List, Optional

from message import Message, Role
from memory import MemoryStrategy

class EntityMemory(MemoryStrategy):
    """Memory strategy that extracts and stores facts/entities.

    It wraps a base memory strategy and extracts user facts (name, preferences)
    using simple regex patterns. The extracted facts are prepended as a system
    message to the context.
    """

    def __init__(self, base_memory: MemoryStrategy) -> None:
        self._base_memory = base_memory
        self._entities: Dict[str, str] = {}

        # Simple regex rules for demo purposes
        self._rules = [
            (re.compile(r"my name is ([\w\s]+)", re.IGNORECASE), "name"),
            (re.compile(r"i like ([\w\s]+)", re.IGNORECASE), "likes"),
            (re.compile(r"i prefer ([\w\s]+)", re.IGNORECASE), "prefers"),
        ]

    def add_message(self, message: Message) -> None:
        if message.role == Role.USER:
            self._extract_entities(message.content)
        self._base_memory.add_message(message)

    def _extract_entities(self, text: str) -> None:
        for pattern, key in self._rules:
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                # For demo purposes, we just append if it already exists, or overwrite.
                # Let's collect a list if multiple things are liked.
                if key in ["likes", "prefers"] and key in self._entities:
                    self._entities[key] += f", {value}"
                else:
                    self._entities[key] = value

    def get_messages(self) -> List[Message]:
        base_messages = self._base_memory.get_messages()

        if not self._entities:
            return base_messages

        facts = []
        if "name" in self._entities:
            facts.append(f"User's name is {self._entities['name']}.")
        if "likes" in self._entities:
            facts.append(f"User likes {self._entities['likes']}.")
        if "prefers" in self._entities:
            facts.append(f"User prefers {self._entities['prefers']}.")

        if facts:
            entity_msg = Message(
                role=Role.SYSTEM,
                content=f"[Extracted Entities]: {' '.join(facts)}"
            )
            return [entity_msg] + base_messages

        return base_messages

    def get_context(self) -> str:
        return self._format_messages(self.get_messages())

    def clear(self) -> None:
        self._entities.clear()
        self._base_memory.clear()
