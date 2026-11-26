from typing import List
import hashlib
import time

try:
    from .crawl_request import CrawlRequest
    from .crawl_result import CrawlResult
    from .url_frontier import UrlFrontier
    from .url_fetcher import UrlFetcher
    from .html_parser import HtmlParser
except ImportError:
    from crawl_request import CrawlRequest
    from crawl_result import CrawlResult
    from url_frontier import UrlFrontier
    from url_fetcher import UrlFetcher
    from html_parser import HtmlParser

class Crawler:
    def __init__(self, frontier: UrlFrontier, fetcher: UrlFetcher, parser: HtmlParser) -> None:
        self.frontier = frontier
        self.fetcher = fetcher
        self.parser = parser
        self.results: List[CrawlResult] = []

    def start(self, seed_urls: List[str], max_depth: int = 1) -> None:
        for url in seed_urls:
            self.frontier.enqueue(CrawlRequest(url, 0))

        while self.frontier.has_next():
            request = self.frontier.dequeue()
            if not request or request.depth > max_depth:
                continue

            try:
                content = self.fetcher.fetch(request)
                links = self.parser.extract_links(content)
                status = 200
            except ValueError:
                content = ""
                links = []
                status = 404
            
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest() if content else ""
            fetched_at = time.time()
            
            result = CrawlResult(request.url, status, content, links, content_hash, fetched_at)
            self.results.append(result)

            if status == 200 and request.depth < max_depth:
                for link in links:
                    self.frontier.enqueue(CrawlRequest(link, request.depth + 1))
