import math
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

class InvertedIndexSearch:
    """
    Inverted index document engine supporting text tokenization, case normalization,
    posting lists with term frequencies, TF-IDF document score ranking, and multi-term boolean search.
    """

    def __init__(self):
        # Maps doc_id to original text
        self.documents: Dict[int, str] = {}
        # Maps term to a dict of {doc_id: term_frequency_count}
        self.index: Dict[str, Dict[int, int]] = defaultdict(dict)
        # Maps doc_id to total number of terms in the document
        self.doc_lengths: Dict[int, int] = {}

    def add_document(self, doc_id: int, text: str) -> None:
        """Analyzes text and adds it to the inverted index."""
        self.documents[doc_id] = text
        tokens = self._tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)

        term_counts = Counter(tokens)
        for term, count in term_counts.items():
            self.index[term][doc_id] = count

    def _tokenize(self, text: str) -> List[str]:
        """Case normalization and simple tokenization."""
        text = text.lower()
        # Remove non-alphanumeric characters
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.split()

    def _tf(self, term: str, doc_id: int) -> float:
        """Term Frequency (TF): Term count / Total terms in document."""
        tf_count = self.index.get(term, {}).get(doc_id, 0)
        doc_length = self.doc_lengths.get(doc_id, 0)
        if doc_length == 0:
            return 0.0
        return tf_count / doc_length

    def _idf(self, term: str) -> float:
        """Inverse Document Frequency (IDF): log(Total documents / Documents containing term)."""
        n_docs = len(self.documents)
        df = len(self.index.get(term, {}))
        if df == 0 or n_docs == 0:
            return 0.0
        # Add 1 to numerator and denominator to avoid log(1) = 0 and div by zero if using variations
        # Here we use standard log(N / df) but adding a base score to ensure matches contribute
        return math.log((1 + n_docs) / (1 + df)) + 1.0

    def search(self, query: str, operator: str = 'OR') -> List[Tuple[int, float]]:
        """
        Searches the index using TF-IDF ranking and returns a list of (doc_id, score)
        sorted by score in descending order.
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        doc_scores: Dict[int, float] = defaultdict(float)

        if operator.upper() == 'AND':
            if not tokens:
                matching_docs = set()
            else:
                matching_docs = set(self.index.get(tokens[0], {}).keys())
                for token in tokens[1:]:
                    matching_docs.intersection_update(self.index.get(token, {}).keys())
        else: # OR
            matching_docs = set()
            for token in tokens:
                matching_docs.update(self.index.get(token, {}).keys())

        for doc_id in matching_docs:
            score = 0.0
            for token in tokens:
                tf = self._tf(token, doc_id)
                idf = self._idf(token)
                score += tf * idf
            if score > 0:
                doc_scores[doc_id] = score

        return sorted(doc_scores.items(), key=lambda x: (-x[1], x[0]))
