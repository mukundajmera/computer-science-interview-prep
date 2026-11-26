import threading
from typing import Dict, List, Optional
import urllib.parse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
from crawl_request import CrawlRequest
sys.path.pop(0)

class ShardQueue:
    def __init__(self) -> None:
        self.shards: Dict[str, List[CrawlRequest]] = {}
        self.lock = threading.Lock()

    def enqueue(self, request: CrawlRequest) -> None:
        host = urllib.parse.urlparse(request.url).netloc
        with self.lock:
            if host not in self.shards:
                self.shards[host] = []
            self.shards[host].append(request)

    def dequeue(self, host: str) -> Optional[CrawlRequest]:
        with self.lock:
            if host in self.shards and self.shards[host]:
                return self.shards[host].pop(0)
            return None
