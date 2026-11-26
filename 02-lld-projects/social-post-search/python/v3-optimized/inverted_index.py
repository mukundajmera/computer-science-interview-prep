from collections import defaultdict
from typing import Dict, List, Set
try:
    from .tokenizer import Tokenizer
except ImportError:
    from tokenizer import Tokenizer

class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.doc_lengths: Dict[str, int] = {}
        self.term_freqs: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total_docs = 0
        self.documents: Dict[str, str] = {}

    def delete_post(self, post_id: str) -> None:
        if post_id not in self.documents:
            return
        
        # Remove from term_freqs and index
        if post_id in self.term_freqs:
            for term in self.term_freqs[post_id]:
                if term in self.index and post_id in self.index[term]:
                    self.index[term].remove(post_id)
                    if not self.index[term]:
                        del self.index[term]
            del self.term_freqs[post_id]
            
        if post_id in self.documents:
            del self.documents[post_id]
        if post_id in self.doc_lengths:
            del self.doc_lengths[post_id]
            
        self.total_docs -= 1

    def index_post(self, post_id: str, content: str) -> None:
        if post_id in self.documents:
            self.delete_post(post_id)

        tokens = Tokenizer.tokenize(content)
        if not tokens:
            self.documents[post_id] = content
            self.doc_lengths[post_id] = 0
            self.total_docs += 1
            return
            
        self.documents[post_id] = content
        self.doc_lengths[post_id] = len(tokens)
        self.total_docs += 1
        for token in tokens:
            self.index[token].add(post_id)
            self.term_freqs[post_id][token] += 1

    def search_term(self, term: str, limit: int = 10) -> List[str]:
        return list(self.index.get(term, set()))[:limit]

