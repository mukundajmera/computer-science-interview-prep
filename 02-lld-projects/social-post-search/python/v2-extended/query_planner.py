from typing import List, Set, Optional
try:
    from .inverted_index import InvertedIndex
    from .tokenizer import Tokenizer
except ImportError:
    from inverted_index import InvertedIndex
    from tokenizer import Tokenizer

class QueryPlanner:
    def __init__(self, index: InvertedIndex):
        self.index = index

    def plan_and_execute(self, raw_query: str) -> List[str]:
        tokens = raw_query.split()
        if not tokens:
            return []

        or_groups = []
        current_and_group = []

        for token in tokens:
            if token.upper() == 'OR':
                if current_and_group:
                    or_groups.append(current_and_group)
                    current_and_group = []
            elif token.upper() == 'AND':
                continue
            else:
                filtered = Tokenizer.tokenize(token)
                if filtered:
                    current_and_group.extend(filtered)

        if current_and_group:
            or_groups.append(current_and_group)

        final_set: Set[str] = set()
        for group in or_groups:
            group_set: Optional[Set[str]] = None
            for term in group:
                term_set = self.index.index.get(term, set())
                if group_set is None:
                    group_set = term_set.copy()
                else:
                    group_set.intersection_update(term_set)
            
            if group_set is not None:
                final_set.update(group_set)

        return list(final_set)
