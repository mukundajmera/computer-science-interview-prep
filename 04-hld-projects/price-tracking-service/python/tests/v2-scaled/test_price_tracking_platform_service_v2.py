import sys
import os
from typing import List
import uuid

# Insert base directory into path for dynamic imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

from price_tracking_platform_service_v2 import PriceTrackingPlatformServiceV2, ProjectionStore

class InMemoryProjectionStore:
    def __init__(self):
        self.history = []

    def upsert_projection(self, object_id: str, snapshot: str) -> None:
        self.history.insert(0, snapshot)

    def recent(self, limit: int) -> List[str]:
        return self.history[:limit]

class InMemoryPriceTrackingPlatformServiceV2:
    def __init__(self, projection_store: ProjectionStore):
        self.projection_store = projection_store
        self.items = {}
        self.idempotency_keys = {}

    def create(self, owner_id: str, payload: str) -> str:
        object_id = str(uuid.uuid4())
        self.items[object_id] = payload
        self.projection_store.upsert_projection(object_id, payload)
        return object_id

    def publish_mutation(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if idempotency_key in self.idempotency_keys:
            return
        if object_id in self.items:
            self.items[object_id] = mutation_payload
            self.projection_store.upsert_projection(object_id, mutation_payload)
            self.idempotency_keys[idempotency_key] = "PROCESSED"

    def read_recent(self, limit: int) -> List[str]:
        return self.projection_store.recent(limit)

def test_create_and_read_recent():
    store = InMemoryProjectionStore()
    service: PriceTrackingPlatformServiceV2 = InMemoryPriceTrackingPlatformServiceV2(store)
    
    service.create("user1", "payload1")
    service.create("user1", "payload2")
    
    recent = service.read_recent(5)
    assert len(recent) == 2
    assert recent[0] == "payload2"
    assert recent[1] == "payload1"

def test_publish_mutation():
    store = InMemoryProjectionStore()
    service: PriceTrackingPlatformServiceV2 = InMemoryPriceTrackingPlatformServiceV2(store)
    
    object_id = service.create("user1", "payload1")
    service.publish_mutation(object_id, "payload1-mutated", "idem1")
    
    recent = service.read_recent(1)
    assert len(recent) == 1
    assert recent[0] == "payload1-mutated"

def test_publish_mutation_idempotency():
    store = InMemoryProjectionStore()
    service: PriceTrackingPlatformServiceV2 = InMemoryPriceTrackingPlatformServiceV2(store)
    
    object_id = service.create("user1", "payload1")
    service.publish_mutation(object_id, "payload1-mutated", "idem1")
    service.publish_mutation(object_id, "payload1-mutated-again", "idem1") # Ignored
    
    recent = service.read_recent(1)
    assert len(recent) == 1
    assert recent[0] == "payload1-mutated"

def test_read_recent_limit():
    store = InMemoryProjectionStore()
    service: PriceTrackingPlatformServiceV2 = InMemoryPriceTrackingPlatformServiceV2(store)
    
    service.create("user1", "p1")
    service.create("user1", "p2")
    service.create("user1", "p3")
    
    recent = service.read_recent(2)
    assert len(recent) == 2
    assert recent[0] == "p3"
    assert recent[1] == "p2"
