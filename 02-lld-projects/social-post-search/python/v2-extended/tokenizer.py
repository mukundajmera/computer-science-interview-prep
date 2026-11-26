import re
from typing import List

class Tokenizer:
    STOP_WORDS = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if t not in cls.STOP_WORDS]
