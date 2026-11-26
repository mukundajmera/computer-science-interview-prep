from typing import Optional, List
try:
    from .inverted_index import InvertedIndex
    from .query_planner import QueryPlanner
    from .search_ranking_service import SearchRankingService
except ImportError:
    from inverted_index import InvertedIndex
    from query_planner import QueryPlanner
    from search_ranking_service import SearchRankingService

class PostIngestionServiceV2:
    def __init__(self):
        self.index = InvertedIndex()
        self.query_planner = QueryPlanner(self.index)
        self.ranking_service = SearchRankingService(self.index)

    def upsert(self, post_id: str, content: str) -> None:
        self.index.index_post(post_id, content)

    def get(self, post_id: str) -> Optional[str]:
        return self.index.documents.get(post_id)

    def delete(self, post_id: str) -> None:
        self.index.delete_post(post_id)

    def search(self, raw_query: str) -> List[str]:
        candidates = self.query_planner.plan_and_execute(raw_query)
        return self.ranking_service.rank(raw_query, candidates)
