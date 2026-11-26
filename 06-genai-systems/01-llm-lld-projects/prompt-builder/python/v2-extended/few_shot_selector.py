from template import PromptTemplate
"""
Dynamic few-shot example selection based on semantic similarity.
"""
from typing import List, Dict, Tuple
import math
from collections import Counter
import re

class FewShotExample:
    def __init__(self, query: str, response: str):
        self.query = query
        self.response = response

    def __repr__(self) -> str:
        return f"FewShotExample(query={self.query!r}, response={self.response!r})"

def tokenize(text: str) -> List[str]:
    """Simple word tokenizer."""
    return re.findall(r'\w+', text.lower())

def cosine_similarity(vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
    """Calculate cosine similarity between two term frequency vectors."""
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(val ** 2 for val in vec1.values())
    sum2 = sum(val ** 2 for val in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

class SemanticFewShotSelector:
    """
    Selects the most relevant few-shot examples using simple BoW cosine similarity.
    """
    def __init__(self, examples: List[FewShotExample]):
        self.examples = examples
        self._vectors = [Counter(tokenize(ex.query)) for ex in examples]

    def select(self, query: str, top_k: int = 3) -> List[FewShotExample]:
        """
        Select the top_k most similar examples to the given query.
        """
        query_vec = Counter(tokenize(query))

        scored_examples: List[Tuple[float, FewShotExample]] = []
        for i, example in enumerate(self.examples):
            score = cosine_similarity(query_vec, self._vectors[i])
            scored_examples.append((score, example))

        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex for score, ex in scored_examples[:top_k]]

class FewShotFormatter:
    """
    Formats a list of FewShotExample objects into a single string using a template.
    """
    def __init__(self, example_template: str):
        self.example_template = example_template

    def format(self, examples: List[FewShotExample]) -> str:
        """
        Format the given examples.
        """
        formatted_examples = []
        for example in examples:
            tpl = PromptTemplate(self.example_template)
            formatted_examples.append(tpl.render({"query": example.query, "response": example.response}))
        return "\n\n".join(formatted_examples)
