import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))

from windowed_top_k_service import WindowedTopKService

class InMemoryWindowedTopKService:
    def __init__(self):
        self.view_counts = {}

    def ingest_view(self, video_id: str, timestamp_ms: int) -> None:
        self.view_counts[video_id] = self.view_counts.get(video_id, 0) + 1

    def top_k(self, window_key: str, k: int) -> list[str]:
        sorted_items = sorted(self.view_counts.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items][:k]

def test_ingest_and_top_k():
    service = InMemoryWindowedTopKService()
    service.ingest_view("vid1", 1000)
    service.ingest_view("vid1", 1001)
    service.ingest_view("vid2", 1002)
    
    top = service.top_k("window1", 10)
    assert len(top) == 2
    assert top[0] == "vid1"
    assert top[1] == "vid2"

def test_top_k_limit():
    service = InMemoryWindowedTopKService()
    service.ingest_view("vid1", 1000)
    service.ingest_view("vid2", 1001)
    service.ingest_view("vid2", 1002)
    service.ingest_view("vid3", 1003)
    service.ingest_view("vid3", 1004)
    service.ingest_view("vid3", 1005)
    
    top = service.top_k("window1", 2)
    assert len(top) == 2
    assert top[0] == "vid3"
    assert top[1] == "vid2"

def test_empty_top_k():
    service = InMemoryWindowedTopKService()
    top = service.top_k("window1", 5)
    assert len(top) == 0
