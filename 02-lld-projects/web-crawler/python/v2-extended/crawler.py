from typing import List, Set
from collections import deque
import urllib.parse
import time
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
    from .content_deduplicator import ContentDeduplicator
except ImportError:
    from url_canonicalizer import UrlCanonicalizer
    from robots_policy import RobotsPolicy
    from politeness_policy import PolitenessPolicy
    from content_deduplicator import ContentDeduplicator

class Crawler:
    def __init__(self, canonicalizer: UrlCanonicalizer, robots: RobotsPolicy, politeness: PolitenessPolicy, deduplicator: ContentDeduplicator, fetcher=None, parser=None) -> None:
        self.canonicalizer = canonicalizer
        self.robots = robots
        self.politeness = politeness
        self.deduplicator = deduplicator
        self.fetcher = fetcher
        self.parser = parser
        self.crawled: List[str] = []
        self.results = []
        self.visited: Set[str] = set()

    def start(self, seed_urls: List[str], max_depth: int) -> None:
        queue: deque = deque()
        
        for url in seed_urls:
            canon_url = self.canonicalizer.canonicalize(url)
            if not canon_url.startswith("http"):
                continue
            if canon_url not in self.visited:
                self.visited.add(canon_url)
                queue.append(CrawlRequest(canon_url, 0))

        while queue:
            req = queue.popleft()
            if req.depth > max_depth:
                continue

            parsed = urllib.parse.urlparse(req.url)
            if not parsed.netloc:
                continue
                
            if not self.robots.is_allowed(req.url):
                continue
                
            self.politeness.wait_for_host(req.url)

            try:
                if self.fetcher:
                    content = self.fetcher.fetch(req)
                else:
                    content = ""
                status = 200
                
                if self.deduplicator.is_duplicate(content):
                    continue
                
                if self.parser:
                    links = self.parser.extract_links(content)
                else:
                    links = []
            except ValueError:
                content = ""
                links = []
                status = 404

            self.crawled.append(req.url)
            self.results.append(CrawlResult(req.url, status, content, links, "", time.time()))

            if status == 200 and req.depth < max_depth:
                for link in links:
                    canon_link = self.canonicalizer.canonicalize(link)
                    if not canon_link.startswith("http"):
                        continue
                    if canon_link not in self.visited:
                        self.visited.add(canon_link)
                        if len(queue) < 10000:
                            queue.append(CrawlRequest(canon_link, req.depth + 1))

    def crawl(self, url: str, content: str) -> bool:
        canonical_url = self.canonicalizer.canonicalize(url)
        if not self.robots.is_allowed(canonical_url):
            return False
        
        self.politeness.wait_for_host(canonical_url)
        
        if self.deduplicator.is_duplicate(content):
            return False
            
        self.crawled.append(canonical_url)
        return True
