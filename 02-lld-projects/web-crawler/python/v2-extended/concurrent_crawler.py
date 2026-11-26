import threading
import time
import urllib.parse
from typing import List, Set
from collections import deque
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
from crawl_request import CrawlRequest
from crawl_result import CrawlResult
from url_fetcher import UrlFetcher
from html_parser import HtmlParser
sys.path.pop(0)

try:
    from .url_canonicalizer import UrlCanonicalizer
    from .robots_policy import RobotsPolicy
    from .politeness_policy import PolitenessPolicy
    from .host_rate_limiter import HostRateLimiter
    from .content_deduplicator import ContentDeduplicator
except ImportError:
    from url_canonicalizer import UrlCanonicalizer
    from robots_policy import RobotsPolicy
    from politeness_policy import PolitenessPolicy
    from host_rate_limiter import HostRateLimiter
    from content_deduplicator import ContentDeduplicator

class ConcurrentCrawler:
    def __init__(self, canonicalizer: UrlCanonicalizer, robots: RobotsPolicy, politeness: PolitenessPolicy, rate_limiter: HostRateLimiter, deduplicator: ContentDeduplicator, fetcher, parser) -> None:
        self.canonicalizer = canonicalizer
        self.robots = robots
        self.politeness = politeness
        self.rate_limiter = rate_limiter
        self.deduplicator = deduplicator
        self.fetcher = fetcher
        self.parser = parser
        self.results = []
        self.visited: Set[str] = set()
        self.queue: deque = deque()
        self.active_tasks = 0
        self.lock = threading.Lock()
        
    def start(self, seed_urls: List[str], max_depth: int, num_threads: int = 4) -> None:
        for url in seed_urls:
            canon = self.canonicalizer.canonicalize(url)
            if canon.startswith("http"):
                self.visited.add(canon)
                self.queue.append(CrawlRequest(canon, 0))
                
        def worker():
            while True:
                with self.lock:
                    if not self.queue and self.active_tasks == 0:
                        break
                    if not self.queue:
                        req = None
                    else:
                        req = self.queue.popleft()
                        
                if not req:
                    time.sleep(0.01)
                    continue
                    
                if req.depth > max_depth:
                    continue
                    
                parsed = urllib.parse.urlparse(req.url)
                host = parsed.netloc
                if not host or not self.robots.is_allowed(req.url):
                    continue
                    
                if not self.rate_limiter.try_acquire(host):
                    with self.lock:
                        self.queue.append(req)
                    # Yield instead of block
                    continue
                    
                with self.lock:
                    self.active_tasks += 1
                    
                try:
                    self.politeness.wait_for_host(req.url)
                    
                    try:
                        content = self.fetcher.fetch(req)
                        status = 200
                        links = []
                        if not self.deduplicator.is_duplicate(content):
                            links = self.parser.extract_links(content)
                    except ValueError:
                        content = ""
                        status = 404
                        links = []
                        
                    with self.lock:
                        self.results.append(CrawlResult(req.url, status, content, links, "", time.time()))
                        
                        if status == 200 and req.depth < max_depth:
                            for link in links:
                                canon_link = self.canonicalizer.canonicalize(link)
                                if canon_link.startswith("http") and len(self.queue) < 10000:
                                    if canon_link not in self.visited:
                                        self.visited.add(canon_link)
                                        self.queue.append(CrawlRequest(canon_link, req.depth + 1))
                finally:
                    self.rate_limiter.release(host)
                    with self.lock:
                        self.active_tasks -= 1
                        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
