import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_web_crawler_service import ScaledWebCrawlerService, JobStatus

def test_priority_frontier_and_domain_scope():
    crawler = ScaledWebCrawlerService()
    seeds = ["http://example.com/seed1", "http://example.com/seed2"]
    crawler.create_job("job1", seeds, "example.com")

    crawler.add_url_to_frontier("http://example.com/high-priority", 1, "example.com")
    crawler.add_url_to_frontier("http://example.com/low-priority", 100, "example.com")
    crawler.add_url_to_frontier("http://outside.com/ignore", 1, "example.com")

    assert crawler.get_frontier_size() == 4

    highest_priority = crawler.poll_frontier()
    assert highest_priority is not None
    assert highest_priority.url == "http://example.com/high-priority"

def test_host_politeness_token_bucket():
    crawler = ScaledWebCrawlerService()
    url = "http://slowhost.com/page"

    # Default bucket capacity is 5, fetch 5 times should succeed
    for i in range(5):
        assert crawler.try_fetch(url) is True

    # 6th time should fail
    assert crawler.try_fetch(url) is False

    # Wait for refill
    time.sleep(1.1)

    # Should succeed again
    assert crawler.try_fetch(url) is True

def test_duplicate_content_fingerprinting():
    crawler = ScaledWebCrawlerService()
    content1 = "This is some unique content."
    content2 = "This is some unique content."
    content3 = "This is completely different."

    assert crawler.is_duplicate_content(content1) is False
    assert crawler.is_duplicate_content(content2) is True
    assert crawler.is_duplicate_content(content3) is False

def test_crawl_job_pause_resume():
    crawler = ScaledWebCrawlerService()
    seeds = ["http://example.com"]
    crawler.create_job("job2", seeds, "example.com")

    assert crawler.get_job_status("job2") == JobStatus.RUNNING

    crawler.pause_job("job2")
    assert crawler.get_job_status("job2") == JobStatus.PAUSED

    crawler.resume_job("job2")
    assert crawler.get_job_status("job2") == JobStatus.RUNNING

    assert crawler.get_job_status("nonexistent") is None
