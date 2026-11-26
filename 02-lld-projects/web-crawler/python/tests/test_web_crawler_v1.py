
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))

from crawl_request import CrawlRequest
from url_frontier import UrlFrontier
from url_fetcher import UrlFetcher
from html_parser import HtmlParser
from crawler import Crawler

class TestV1(unittest.TestCase):
    def test_frontier_deduplication(self) -> None:
        frontier = UrlFrontier()
        frontier.enqueue(CrawlRequest("http://example.com"))
        frontier.enqueue(CrawlRequest("http://example.com"))
        self.assertEqual(len(frontier.queue), 1)
        
    def test_html_parser(self) -> None:
        parser = HtmlParser()
        links = parser.extract_links("<html><a href='http://link1.com'>Link</a></html>")
        self.assertEqual(links, ["http://link1.com"])
        
    def test_crawler_flow(self) -> None:
        frontier = UrlFrontier()
        offline_graph = {"http://example.com": "<html><a href='http://example.com/next'>Next</a></html>"}
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        crawl = Crawler(frontier, fetcher, parser)
        crawl.start(["http://example.com"], max_depth=1)
        
        self.assertTrue(len(crawl.results) > 0)
        self.assertEqual(crawl.results[0].url, "http://example.com")
        self.assertTrue(len(crawl.results[0].links) > 0)

    def test_offline_graph_cycles(self) -> None:
        offline_graph = {
            "http://example.com/a": "<html><body><a href='http://example.com/b'>B</a></body></html>",
            "http://example.com/b": "<html><body><a href='http://example.com/a/'>A</a></body></html>"
        }
        
        frontier = UrlFrontier()
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        crawl = Crawler(frontier, fetcher, parser)
        
        crawl.start(["http://example.com/a"], max_depth=5)
        
        self.assertEqual(len(crawl.results), 2)
        urls = {r.url for r in crawl.results}
        self.assertIn("http://example.com/a", urls)
        self.assertIn("http://example.com/b", urls)
        
    def test_malformed_url_and_404(self) -> None:
        offline_graph = {
            "http://start.com": "<html><a href='not_http://bad.com'>Bad</a><a href='http://missing.com'>Missing</a></html>"
        }
        
        frontier = UrlFrontier()
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        crawl = Crawler(frontier, fetcher, parser)
        
        crawl.start(["http://start.com"], max_depth=2)
        
        self.assertEqual(len(crawl.results), 2)
        urls = {r.url for r in crawl.results}
        self.assertIn("http://start.com", urls)
        self.assertIn("http://missing.com", urls)
        
        missing_res = next(r for r in crawl.results if r.url == "http://missing.com")
        self.assertEqual(missing_res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
