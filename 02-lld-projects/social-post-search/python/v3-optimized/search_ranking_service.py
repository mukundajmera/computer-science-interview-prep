import math
from typing import List, Dict, Tuple
try:
    from .inverted_index import InvertedIndex
    from .tokenizer import Tokenizer
except ImportError:
    from inverted_index import InvertedIndex
    from tokenizer import Tokenizer

class SearchRankingService:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def rank(self, raw_query: str, candidate_post_ids: List[str]) -> List[str]:
        query_terms = Tokenizer.tokenize(raw_query)
        if not query_terms or not candidate_post_ids:
            return candidate_post_ids
        
        avgdl = 0
        if self.index.total_docs > 0:
            avgdl = sum(self.index.doc_lengths.values()) / self.index.total_docs

        scores: List[Tuple[str, float]] = []
        for post_id in candidate_post_ids:
            score = 0.0
            doc_len = self.index.doc_lengths.get(post_id, 0)
            for term in query_terms:
                tf = self.index.term_freqs.get(post_id, {}).get(term, 0)
                if tf == 0:
                    continue
                df = len(self.index.index.get(term, set()))
                N = self.index.total_docs
                idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
                term_score = idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / (avgdl or 1))))
                score += term_score
            scores.append((post_id, score))

        scores.sort(key=lambda x: (-x[1], x[0]))
        return [pid for pid, _ in scores]

