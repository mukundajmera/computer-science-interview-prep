from typing import Set, Optional
from collections import deque

try:
    from .crawl_request import CrawlRequest
except ImportError:
    from crawl_request import CrawlRequest

class UrlFrontier:
    def __init__(self) -> None:
        self.queue: deque[CrawlRequest] = deque()
        self.visited: Set[str] = set()

    def _normalize_url(self, url: str) -> str:
        norm = url.strip().lower()
        if norm.endswith('/'):
            norm = norm[:-1]
        return norm

    def enqueue(self, request: CrawlRequest) -> None:
        if not request.url.startswith("http"):
            return
        
        if len(self.queue) >= 10000:
            return

        normalized_url = self._normalize_url(request.url)
        if normalized_url not in self.visited:
            self.visited.add(normalized_url)
            # update URL on request
            request.url = normalized_url
            self.queue.append(request)

    def dequeue(self) -> Optional[CrawlRequest]:
        if self.queue:
            return self.queue.popleft()
        return None

    def has_next(self) -> bool:
        return len(self.queue) > 0
