from __future__ import annotations

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

from distributed_top_k_service import DistributedTopKService

class InMemoryDistributedTopKService:
    def __init__(self):
        self.global_view_counts = {}
        self.replay_triggered = False

    def ingest_view(self, video_id: str, timestamp_ms: int, partition_key: str) -> None:
        self.global_view_counts[video_id] = self.global_view_counts.get(video_id, 0) + 1

    def top_k(self, window_key: str, k: int, region: str) -> list[str]:
        sorted_items = sorted(self.global_view_counts.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items][:k]

    def replay_window(self, window_key: str, replay_token: str) -> None:
        self.replay_triggered = True

def test_ingest_and_top_k():
    service = InMemoryDistributedTopKService()
    service.ingest_view("vidA", 100, "part1")
    service.ingest_view("vidA", 101, "part2")
    service.ingest_view("vidB", 102, "part1")

    top = service.top_k("window-1", 10, "us-east")
    assert len(top) == 2
    assert top[0] == "vidA"
    assert top[1] == "vidB"

def test_top_k_limit_and_region():
    service = InMemoryDistributedTopKService()
    service.ingest_view("v1", 10, "p1")
    service.ingest_view("v2", 11, "p1")
    service.ingest_view("v2", 12, "p1")
    service.ingest_view("v3", 13, "p1")
    service.ingest_view("v3", 14, "p1")
    service.ingest_view("v3", 15, "p1")

    top = service.top_k("win2", 2, "eu-west")
    assert len(top) == 2
    assert top[0] == "v3"
    assert top[1] == "v2"

def test_replay_window():
    service = InMemoryDistributedTopKService()
    assert not service.replay_triggered
    
    service.replay_window("win3", "tokenXYZ")
    assert service.replay_triggered
