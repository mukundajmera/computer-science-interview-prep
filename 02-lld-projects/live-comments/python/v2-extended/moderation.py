from typing import Set

class BasicModerationPipeline:
    def __init__(self, blocked_words: Set[str]):
        self.blocked_words = blocked_words

    def is_approved(self, payload: str) -> bool:
        if not payload or not payload.strip():
            return False
        lower_payload = payload.lower()
        for word in self.blocked_words:
            if word.lower() in lower_payload:
                return False
        return True
