import sys
import os
import threading
import time
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))

from url_fetcher import UrlFetcher
from html_parser import HtmlParser
from crawl_request import CrawlRequest
from url_canonicalizer import UrlCanonicalizer
from robots_policy import RobotsPolicy
from politeness_policy import PolitenessPolicy

sys.path.pop(0)
sys.path.pop(0)

try:
    from .shard_queue import ShardQueue
    from .fingerprint_store import FingerprintStore
    from .backpressure_controller import BackpressureController
except ImportError:
    from shard_queue import ShardQueue
    from fingerprint_store import FingerprintStore
    from backpressure_controller import BackpressureController

class Crawler:
    def __init__(self, queue: ShardQueue, store: FingerprintStore, backpressure: BackpressureController, fetcher: UrlFetcher, parser: HtmlParser, canonicalizer: UrlCanonicalizer, politeness: PolitenessPolicy, robots: RobotsPolicy) -> None:
        self.queue = queue
        self.store = store
        self.backpressure = backpressure
        self.fetcher = fetcher
        self.parser = parser
        self.canonicalizer = canonicalizer
        self.politeness = politeness
        self.robots = robots
        self.completed: List[str] = []
        self.lock = threading.Lock()
        self.running = True
        
    def cancel(self) -> None:
        self.running = False
        
    def start(self, seed_urls: List[str], host: str, max_tasks: int, num_threads: int, max_depth: int = 2) -> None:
        for url in seed_urls:
            self.queue.enqueue(CrawlRequest(url, 0))
            
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self.worker, args=(host, max_tasks // num_threads, max_depth))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()

    def worker(self, host: str, num_tasks: int, max_depth: int) -> None:
        tasks_done = 0
        idle_tries = 0
        while tasks_done < num_tasks and self.running:
            if self.backpressure.acquire():
                try:
                    req = self.queue.dequeue(host)
                    if req and req.depth <= max_depth:
                        idle_tries = 0
                        canonical_url = self.canonicalizer.canonicalize(req.url)
                        if self.robots.is_allowed(canonical_url) and self.store.add(canonical_url):
                            self.politeness.wait_for_host(canonical_url)
                            try:
                                content = self.fetcher.fetch(CrawlRequest(canonical_url, req.depth))
                                links = self.parser.extract_links(content)
                                if req.depth < max_depth:
                                    for link in links:
                                        self.queue.enqueue(CrawlRequest(link, req.depth + 1))
                            except ValueError:
                                pass
                        
                        with self.lock:
                            self.completed.append(req.url)
                        tasks_done += 1
                    else:
                        idle_tries += 1
                        if idle_tries >= 10:
                            break
                        time.sleep(0.01)
                finally:
                    self.backpressure.release()
            else:
                time.sleep(0.01)
