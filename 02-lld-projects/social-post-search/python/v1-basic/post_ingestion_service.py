import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class PostIngestionService:
    def __init__(self):
        # post_id -> content
        self.posts: Dict[str, str] = {}
        # Inverted index: term -> set of post_ids
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        # Term frequency for ranking: (post_id, term) -> count
        self.term_freq: Dict[Tuple[str, str], int] = defaultdict(int)
        
        self.stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}

    def _tokenize_and_filter(self, content: str) -> List[str]:
        # Convert to lowercase and split by non-alphanumeric
        tokens = re.findall(r'\b\w+\b', content.lower())
        # Stop-word filtering
        return [t for t in tokens if t not in self.stop_words]

    def ingest_post(self, post_id: str, content: str):
        self.posts[post_id] = content
        
        tokens = self._tokenize_and_filter(content)
        
        for token in tokens:
            self.inverted_index[token].add(post_id)
            self.term_freq[(post_id, token)] += 1

    def search_and(self, query: str) -> List[str]:
        tokens = self._tokenize_and_filter(query)
        if not tokens:
            return []
            
        result_set = self.inverted_index.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            result_set.intersection_update(self.inverted_index.get(token, set()))
            
        return self._rank_results(list(result_set), tokens)

    def search_or(self, query: str) -> List[str]:
        tokens = self._tokenize_and_filter(query)
        if not tokens:
            return []
            
        result_set = set()
        for token in tokens:
            result_set.update(self.inverted_index.get(token, set()))
            
        return self._rank_results(list(result_set), tokens)

    def _rank_results(self, post_ids: List[str], query_tokens: List[str]) -> List[str]:
        # Relevance ranking based on simple term frequency sum
        def score(pid: str) -> int:
            return sum(self.term_freq[(pid, token)] for token in query_tokens)
            
        # Sort by score descending, then by post_id descending for stability
        ranked = sorted(post_ids, key=lambda pid: (score(pid), pid), reverse=True)
        return ranked

