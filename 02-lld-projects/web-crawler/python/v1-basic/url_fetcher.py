try:
    from .crawl_request import CrawlRequest
except ImportError:
    from crawl_request import CrawlRequest

from typing import Dict, Optional

class UrlFetcher:
    def __init__(self, offline_graph: Optional[Dict[str, str]] = None) -> None:
        self.offline_graph = offline_graph or {}
        
    def fetch(self, request: CrawlRequest) -> str:
        if request.url in self.offline_graph:
            return self.offline_graph[request.url]
        raise ValueError(f"404 Not Found: {request.url}")
