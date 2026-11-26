
import unittest
import sys
import os

if 'crawler' in sys.modules:
    del sys.modules['crawler']

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))
from crawl_request import CrawlRequest
from url_fetcher import UrlFetcher
from html_parser import HtmlParser
from url_canonicalizer import UrlCanonicalizer
from robots_policy import RobotsPolicy
from politeness_policy import PolitenessPolicy
sys.path.pop(0)
sys.path.pop(0)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v3-optimized')))
from shard_queue import ShardQueue
from fingerprint_store import FingerprintStore
from backpressure_controller import BackpressureController
from crawl_coordinator import CrawlCoordinator
from crawler import Crawler
sys.path.pop(0)

class TestV3(unittest.TestCase):
    def test_shard_queue(self) -> None:
        q = ShardQueue()
        q.enqueue(CrawlRequest("http://a.com/1", 0))
        q.enqueue(CrawlRequest("http://b.com/1", 0))
        self.assertEqual(q.dequeue("a.com").url, "http://a.com/1")
        self.assertIsNone(q.dequeue("a.com"))
        
    def test_fingerprint_store(self) -> None:
        store = FingerprintStore()
        self.assertTrue(store.add("hash1"))
        self.assertFalse(store.add("hash1"))
        
    def test_coordinator(self) -> None:
        q = ShardQueue()
        for i in range(10):
            q.enqueue(CrawlRequest(f"http://example.com/{i}", 0))
            
        bp = BackpressureController(max_concurrent=2)
        coord = CrawlCoordinator(q, bp)
        coord.run_concurrently("example.com", num_tasks=10, num_threads=2)
        
        self.assertEqual(len(coord.completed), 10)
        
    def test_crawler_flow(self) -> None:
        offline_graph = {
            "http://example.com/a": "<html><a href='http://example.com/b'>B</a></html>",
            "http://example.com/b": "<html><a href='http://example.com/a'>A</a></html>"
        }
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        canonicalizer = UrlCanonicalizer()
        robots = RobotsPolicy()
        politeness = PolitenessPolicy(delay_ms=0)
        
        queue = ShardQueue()
        store = FingerprintStore()
        backpressure = BackpressureController(max_concurrent=2)
        
        crawler = Crawler(queue, store, backpressure, fetcher, parser, canonicalizer, politeness, robots)
        crawler.start(["http://example.com/a"], "example.com", 2, 1, max_depth=1)
        
        self.assertEqual(len(crawler.completed), 2)
        self.assertIn("http://example.com/a", crawler.completed)
        
    def test_crawler_flow_edges_and_cancellation(self) -> None:
        offline_graph = {
            "http://example.com/start": "<html><a href='http://example.com/cycle1'>Cycle 1</a><a href='bad://url'>Bad</a><a href='http://example.com/notfound'>Not Found</a></html>",
            "http://example.com/cycle1": "<html><a href='http://example.com/start'>Start</a><a href='http://example.com/deep'>Deep</a></html>",
            "http://example.com/deep": "<html><a href='http://example.com/deeper'>Deeper</a></html>"
        }
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        canonicalizer = UrlCanonicalizer()
        robots = RobotsPolicy()
        politeness = PolitenessPolicy(delay_ms=0)
        
        queue = ShardQueue()
        store = FingerprintStore()
        backpressure = BackpressureController(max_concurrent=5)
        
        crawler = Crawler(queue, store, backpressure, fetcher, parser, canonicalizer, politeness, robots)
        crawler.start(["http://example.com/start"], "example.com", 10, 1, max_depth=1)
        
        completed_urls = set(crawler.completed)
        self.assertIn("http://example.com/start", completed_urls)
        self.assertIn("http://example.com/cycle1", completed_urls)
        
        crawler.cancel()
        self.assertFalse(crawler.running)

if __name__ == "__main__":
    unittest.main()
