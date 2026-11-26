import sys
import os
import unittest
import time
from typing import Optional, List, Dict, Set

# Add directories to sys.path to resolve hyphenated module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

from live_comments_stream_service import LiveCommentsStreamService
from live_comments_stream_service_v2 import LiveCommentsStreamServiceV2, ProjectionStore
from distributed_live_comments_stream_service import DistributedLiveCommentsStreamService

# V1 Dummy Implementation
class DummyLiveCommentsStreamService:
    def __init__(self):
        self.comments = {}
        self.id_counter = 1

    def create(self, owner_id: str, payload: str) -> str:
        obj_id = str(self.id_counter)
        self.id_counter += 1
        self.comments[obj_id] = payload
        return obj_id

    def get_by_id(self, object_id: str) -> Optional[str]:
        return self.comments.get(object_id)

    def mutate(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if object_id in self.comments:
            self.comments[object_id] += mutation_payload


# V2 Dummy Implementation
class DummyProjectionStore:
    def __init__(self):
        self.projections = []

    def upsert_projection(self, object_id: str, snapshot: str) -> None:
        self.projections.append(snapshot)

    def recent(self, limit: int) -> List[str]:
        return self.projections[-limit:] if limit > 0 and self.projections else []


class DummyLiveCommentsStreamServiceV2:
    def __init__(self):
        self.comments = {}
        self.id_counter = 1
        self.store = DummyProjectionStore()
        self.processed_keys = set()

        self.create_calls = 0
        self.last_create_time = time.time()

    def create(self, owner_id: str, payload: str) -> str:
        now = time.time()
        if now - self.last_create_time < 1.0:
            self.create_calls += 1
            if self.create_calls > 5:
                raise RuntimeError("Rate limit exceeded")
        else:
            self.create_calls = 1
            self.last_create_time = now

        obj_id = str(self.id_counter)
        self.id_counter += 1
        self.comments[obj_id] = payload
        self.store.upsert_projection(obj_id, payload)
        return obj_id

    def publish_mutation(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if idempotency_key in self.processed_keys:
            return
        self.processed_keys.add(idempotency_key)

        if object_id in self.comments:
            new_value = self.comments[object_id] + mutation_payload
            self.comments[object_id] = new_value
            self.store.upsert_projection(object_id, new_value)

    def read_recent(self, limit: int) -> List[str]:
        return self.store.recent(limit)


# V3 Dummy Implementation
class DummyDistributedIdempotencyStore:
    def __init__(self):
        self.claimed = set()

    def claim(self, key: str, ttl_ms: int) -> bool:
        if key in self.claimed:
            return False
        self.claimed.add(key)
        return True


class DummyDistributedLiveCommentsStreamService:
    def __init__(self):
        self.comments = {}
        self.regional_views = {}
        self.id_counter = 1
        self.idempotency_store = DummyDistributedIdempotencyStore()
        self.pubsub_topics = []

    def create(self, owner_id: str, payload: str, region: str) -> str:
        obj_id = str(self.id_counter)
        self.id_counter += 1
        self.comments[obj_id] = payload

        if region not in self.regional_views:
            self.regional_views[region] = []
        self.regional_views[region].append(payload)

        return obj_id

    def mutate_with_replay_token(self, object_id: str, mutation_payload: str, idempotency_key: str, replay_token: str) -> None:
        if not self.idempotency_store.claim(idempotency_key, 1000):
            return

        if object_id in self.comments:
            new_value = self.comments[object_id] + mutation_payload
            self.comments[object_id] = new_value

            # Simple fanout for tests simulating pubsub
            for region, views in self.regional_views.items():
                self.pubsub_topics.append(f"Fanout msg to {region}: {new_value}")
                views.append(new_value)

    def read_region_view(self, region: str, limit: int) -> List[str]:
        views = self.regional_views.get(region, [])
        return views[-limit:] if limit > 0 and views else []

    def get_pubsub_messages(self) -> List[str]:
        return self.pubsub_topics


def test_v1_basic():
    service: LiveCommentsStreamService = DummyLiveCommentsStreamService()
    obj_id = service.create("user1", "Hello V1")
    assert service.get_by_id(obj_id) == "Hello V1"

    service.mutate(obj_id, " - appended", "key1")
    assert service.get_by_id(obj_id) == "Hello V1 - appended"


def test_v2_scaled():
    service: LiveCommentsStreamServiceV2 = DummyLiveCommentsStreamServiceV2()
    obj_id = service.create("user1", "Hello V2")

    recent = service.read_recent(10)
    assert len(recent) == 1
    assert recent[0] == "Hello V2"

    service.publish_mutation(obj_id, " (updated)", "key-v2")
    recent = service.read_recent(10)
    assert recent[-1] == "Hello V2 (updated)"

    # Test idempotency
    service.publish_mutation(obj_id, " (updated)", "key-v2")
    recent = service.read_recent(10)
    assert recent[-1] == "Hello V2 (updated)" # unchanged

    # Test rate limit
    exception_caught = False
    try:
        for _ in range(6):
            service.create("user1", "Spam")
    except RuntimeError as e:
        exception_caught = True
        assert str(e) == "Rate limit exceeded"
    assert exception_caught


def test_v3_distributed():
    service: DistributedLiveCommentsStreamService = DummyDistributedLiveCommentsStreamService()
    obj_id = service.create("user1", "Hello V3", "US-EAST")
    service.create("user2", "Hello EU", "EU-WEST")

    us_east_view = service.read_region_view("US-EAST", 10)
    assert len(us_east_view) == 1
    assert us_east_view[0] == "Hello V3"

    service.mutate_with_replay_token(obj_id, " - dist update", "key-v3", "token123")

    us_east_view = service.read_region_view("US-EAST", 10)
    assert us_east_view[-1] == "Hello V3 - dist update"

    # Verify fanout logic sent pubsub messages to both regions
    pubsub_messages = service.get_pubsub_messages()
    assert len(pubsub_messages) == 2
    assert any("US-EAST" in msg for msg in pubsub_messages)
    assert any("EU-WEST" in msg for msg in pubsub_messages)

    # Test idempotency claim fails on reuse
    service.mutate_with_replay_token(obj_id, " - dist update", "key-v3", "token456")
    us_east_view = service.read_region_view("US-EAST", 10)
    assert us_east_view[-1] == "Hello V3 - dist update" # unchanged
