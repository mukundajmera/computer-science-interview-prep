import collections
import time
from urllib.parse import urlparse

class MockFetcher:
    def fetch(self, url: str) -> str:
        return f"Content of {url}"

class MockExtractor:
    def extract(self, url: str, content: str) -> list:
        return []

class WebCrawlerService:
    def __init__(self, fetcher=None, extractor=None, politeness_delay_ms=100, max_depth=3):
        self.fetcher = fetcher or MockFetcher()
        self.extractor = extractor or MockExtractor()
        self.politeness_delay_ms = politeness_delay_ms
        self.max_depth = max_depth
        self.seen_urls = set()
        # FIFO Queue for (url, depth)
        self.frontier = collections.deque()
        self.last_fetch_time_per_domain = {}
        self.crawled_results = []
        self.disallowed_urls = set()

    def add_disallowed_rule(self, url: str):
        """Simulates robots.txt disallow check by marking specific URLs as disallowed."""
        self.disallowed_urls.add(url)

    def is_allowed(self, url: str) -> bool:
        """Simulates robots.txt disallow check."""
        return url not in self.disallowed_urls

    def crawl(self, seed_urls: list):
        for url in seed_urls:
            self.frontier.append((url, 0))

        while self.frontier:
            url, depth = self.frontier.popleft()

            if url in self.seen_urls:
                continue

            if not self.is_allowed(url):
                self.seen_urls.add(url)
                continue

            domain = urlparse(url).netloc
            last_fetch_time = self.last_fetch_time_per_domain.get(domain, 0)
            current_time = time.time() * 1000

            if current_time - last_fetch_time < self.politeness_delay_ms:
                # Wait for the remaining time
                time.sleep((self.politeness_delay_ms - (current_time - last_fetch_time)) / 1000.0)

            # Fetch content
            try:
                content = self.fetcher.fetch(url)
                self.crawled_results.append((url, content))
                self.seen_urls.add(url)
                self.last_fetch_time_per_domain[domain] = time.time() * 1000

                if depth < self.max_depth:
                    links = self.extractor.extract(url, content)
                    for link in links:
                        if link not in self.seen_urls:
                            self.frontier.append((link, depth + 1))
            except Exception as e:
                # Handle fetch error, still mark as seen to avoid infinite loop
                self.seen_urls.add(url)
