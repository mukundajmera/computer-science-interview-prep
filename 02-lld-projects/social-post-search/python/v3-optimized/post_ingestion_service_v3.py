from typing import Optional, List, Dict
try:
    from .inverted_index import InvertedIndex
    from .query_planner import QueryPlanner
    from .search_ranking_service import SearchRankingService
except ImportError:
    from inverted_index import InvertedIndex
    from query_planner import QueryPlanner
    from search_ranking_service import SearchRankingService

class PostIngestionServiceV3:
    def __init__(self):
        self.index = InvertedIndex()
        self.query_planner = QueryPlanner(self.index)
        self.ranking_service = SearchRankingService(self.index)
        self.idempotency_keys: Dict[str, float] = {}

    def upsert(self, post_id: str, content: str, idempotency_key: str, region: str) -> bool:
        import time
        current_time = time.time()
        
        # Simple idempotency check (60s TTL)
        if idempotency_key in self.idempotency_keys:
            if current_time - self.idempotency_keys[idempotency_key] < 60:
                return False
                
        self.idempotency_keys[idempotency_key] = current_time
        
        # In a real distributed system, we'd route based on region.
        # Here we just index it.
        self.index.index_post(post_id, content)
        return True

    def delete(self, post_id: str, region: str) -> None:
        self.index.delete_post(post_id)

    def get(self, post_id: str, region: str) -> Optional[str]:
        return self.index.documents.get(post_id)
        
    def search(self, raw_query: str, region: str) -> List[str]:
        candidates = self.query_planner.plan_and_execute(raw_query)
        return self.ranking_service.rank(raw_query, candidates)

