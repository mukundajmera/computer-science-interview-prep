import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass
class TrieNode:
    children: Dict[str, 'TrieNode'] = field(default_factory=dict)
    is_terminal: bool = False
    frequency: int = 0
    top_suggestions: List[Dict[str, int]] = field(default_factory=list)

class SearchAutocompleteService:
    MAX_PREFIX_LENGTH = 50
    TOP_K = 5

    def __init__(self, profanity_blacklist: Optional[Set[str]] = None):
        self.root = TrieNode()
        self.profanity_blacklist = profanity_blacklist or set()
        self.query_counts = defaultdict(int)
        self.lock = threading.Lock()

    def add_query_log(self, query: str) -> None:
        if not query or not query.strip():
            return
        
        clean_query = query.lower()
        if self._is_profane(clean_query):
            return
            
        with self.lock:
            self.query_counts[clean_query] += 1

    def _is_profane(self, query: str) -> bool:
        for word in query.split():
            if word in self.profanity_blacklist:
                return True
        return False

    def rebuild_trie(self) -> None:
        new_root = TrieNode()
        
        with self.lock:
            current_counts = dict(self.query_counts)
            
        for query, freq in current_counts.items():
            if self._is_profane(query):
                continue
            self._insert_query(new_root, query, freq)
            
        self._precompute_top_suggestions(new_root, "")
        
        with self.lock:
            self.root = new_root

    def _insert_query(self, root: TrieNode, query: str, freq: int) -> None:
        curr = root
        for char in query:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
        curr.is_terminal = True
        curr.frequency = freq

    def _precompute_top_suggestions(self, node: TrieNode, prefix: str) -> List[Dict[str, int]]:
        all_suggestions = []
        
        if node.is_terminal:
            all_suggestions.append({"query": prefix, "frequency": node.frequency})
            
        for char, child_node in node.children.items():
            all_suggestions.extend(self._precompute_top_suggestions(child_node, prefix + char))
            
        # Sort by frequency descending, then lexicographically for tie-breaking
        all_suggestions.sort(key=lambda x: (-x["frequency"], x["query"]))
        
        node.top_suggestions = all_suggestions[:self.TOP_K]
        return node.top_suggestions

    def get_suggestions(self, prefix: str) -> List[str]:
        if not prefix:
            return []
            
        clean_prefix = prefix.lower()
        if len(clean_prefix) > self.MAX_PREFIX_LENGTH:
            clean_prefix = clean_prefix[:self.MAX_PREFIX_LENGTH]
            
        with self.lock:
            curr = self.root
            for char in clean_prefix:
                if char not in curr.children:
                    return []
                curr = curr.children[char]
                
            return [s["query"] for s in curr.top_suggestions]
