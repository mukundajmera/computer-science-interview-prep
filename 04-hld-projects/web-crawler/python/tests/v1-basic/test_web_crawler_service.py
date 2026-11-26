import os
import sys
import time

# dynamic sys.path import to avoid ImportErrors with hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from web_crawler_service import WebCrawlerService

class MockExtractorWithMapping:
    def __init__(self, mapping):
        self.mapping = mapping

    def extract(self, url, content):
        return self.mapping.get(url, [])

def test_web_crawler_basic():
    crawler = WebCrawlerService(politeness_delay_ms=0, max_depth=1)
    crawler.crawl(["http://example.com/1", "http://example.com/2"])

    assert len(crawler.seen_urls) == 2
    assert "http://example.com/1" in crawler.seen_urls
    assert "http://example.com/2" in crawler.seen_urls

def test_web_crawler_deduplication():
    crawler = WebCrawlerService(politeness_delay_ms=0, max_depth=1)
    # The same URL is provided twice in the seed
    crawler.crawl(["http://example.com/1", "http://example.com/1"])

    assert len(crawler.seen_urls) == 1
    assert len(crawler.crawled_results) == 1

def test_web_crawler_depth_limiter():
    mapping = {
        "http://example.com/1": ["http://example.com/2"],
        "http://example.com/2": ["http://example.com/3"],
        "http://example.com/3": ["http://example.com/4"]
    }
    extractor = MockExtractorWithMapping(mapping)

    crawler = WebCrawlerService(extractor=extractor, politeness_delay_ms=0, max_depth=1)
    crawler.crawl(["http://example.com/1"])

    # Depth 0: http://example.com/1
    # Depth 1: http://example.com/2
    # Since max_depth is 1, http://example.com/3 should not be processed
    assert len(crawler.seen_urls) == 2
    assert "http://example.com/1" in crawler.seen_urls
    assert "http://example.com/2" in crawler.seen_urls
    assert "http://example.com/3" not in crawler.seen_urls

def test_web_crawler_politeness_delay():
    crawler = WebCrawlerService(politeness_delay_ms=200, max_depth=1)
    start_time = time.time()
    crawler.crawl(["http://example.com/1", "http://example.com/2"])
    end_time = time.time()

    # The first URL doesn't wait. The second URL waits for 200ms.
    assert (end_time - start_time) >= 0.2

def test_web_crawler_robots_txt():
    crawler = WebCrawlerService(politeness_delay_ms=0, max_depth=1)
    crawler.add_disallowed_rule("http://example.com/secret")

    crawler.crawl(["http://example.com/public", "http://example.com/secret"])

    # Secret URL is marked as seen so it isn't picked up again, but it shouldn't have been crawled.
    assert "http://example.com/secret" in crawler.seen_urls
    assert "http://example.com/public" in crawler.seen_urls

    # Check crawled results to ensure secret wasn't fetched
    crawled_urls = [url for url, content in crawler.crawled_results]
    assert "http://example.com/public" in crawled_urls
    assert "http://example.com/secret" not in crawled_urls
