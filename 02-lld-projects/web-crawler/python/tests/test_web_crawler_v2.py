import unittest
import sys
import os

if 'crawler' in sys.modules:
    del sys.modules['crawler']
if 'concurrent_crawler' in sys.modules:
    del sys.modules['concurrent_crawler']

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))

from url_canonicalizer import UrlCanonicalizer
from robots_policy import RobotsPolicy
from politeness_policy import PolitenessPolicy
from content_deduplicator import ContentDeduplicator
from host_rate_limiter import HostRateLimiter
from crawler import Crawler
from concurrent_crawler import ConcurrentCrawler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
from url_fetcher import UrlFetcher
from html_parser import HtmlParser
sys.path.pop(0)

class TestV2(unittest.TestCase):
    def test_canonicalizer(self) -> None:
        canon = UrlCanonicalizer()
        res = canon.canonicalize("HTTP://Example.COM:80/path#frag")
        self.assertEqual(res, "http://example.com:80/path")
        
    def test_robots_policy(self) -> None:
        robots = RobotsPolicy()
        robots.add_rule("example.com", "/private")
        self.assertTrue(robots.is_allowed("http://example.com/public"))
        self.assertFalse(robots.is_allowed("http://example.com/private/data"))

    def test_crawler_flow(self):
        canon = UrlCanonicalizer()
        robots = RobotsPolicy()
        politeness = PolitenessPolicy(delay_ms=0)
        dedup = ContentDeduplicator()
        
        offline_graph = {
            "http://example.com": "<html><a href='http://example.com/2'>Next</a></html>",
            "http://example.com/2": "<html><a href='http://example.com'>Next</a></html>"
        }
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        
        crawl = Crawler(canon, robots, politeness, dedup, fetcher, parser)
        crawl.start(["http://example.com"], 5)
        
        self.assertEqual(len(crawl.results), 2)
        visited_urls = {r.url for r in crawl.results}
        self.assertTrue("http://example.com" in visited_urls)
        self.assertTrue("http://example.com/2" in visited_urls)

    def test_concurrent_crawler(self):
        canon = UrlCanonicalizer()
        robots = RobotsPolicy()
        politeness = PolitenessPolicy(delay_ms=0)
        rate_limiter = HostRateLimiter(max_concurrent=2)
        dedup = ContentDeduplicator()
        
        offline_graph = {
            "http://example.com/1": "<html><a href='http://example.com/2'>2</a></html>",
            "http://example.com/2": "<html><a href='http://example.com/3'>3</a></html>",
            "http://example.com/3": "<html><a href='http://example.com/1'>1</a></html>"
        }
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        
        crawler = ConcurrentCrawler(canon, robots, politeness, rate_limiter, dedup, fetcher, parser)
        crawler.start(["http://example.com/1"], 5, num_threads=2)
        
        self.assertEqual(len(crawler.results), 3)

if __name__ == "__main__":
    unittest.main()
