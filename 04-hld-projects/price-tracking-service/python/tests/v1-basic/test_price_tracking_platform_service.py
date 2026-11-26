import sys
import os
from typing import Optional
import uuid

# Insert base directory into path for dynamic imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from price_tracking_platform_service import PriceTrackingPlatformService

class InMemoryPriceTrackingPlatformService:
    def __init__(self):
        self.items = {}
        self.idempotency_keys = {}

    def create(self, owner_id: str, payload: str) -> str:
        object_id = str(uuid.uuid4())
        self.items[object_id] = payload
        return object_id

    def get_by_id(self, object_id: str) -> Optional[str]:
        return self.items.get(object_id)

    def mutate(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if idempotency_key in self.idempotency_keys:
            return
        if object_id in self.items:
            self.items[object_id] = mutation_payload
            self.idempotency_keys[idempotency_key] = "PROCESSED"

def test_create_and_get():
    service: PriceTrackingPlatformService = InMemoryPriceTrackingPlatformService()
    object_id = service.create("user1", "payload1")
    assert object_id is not None
    
    result = service.get_by_id(object_id)
    assert result == "payload1"

def test_mutate_updates_payload():
    service: PriceTrackingPlatformService = InMemoryPriceTrackingPlatformService()
    object_id = service.create("user1", "payload1")
    
    service.mutate(object_id, "payload2", "idem1")
    result = service.get_by_id(object_id)
    assert result == "payload2"

def test_mutate_idempotency():
    service: PriceTrackingPlatformService = InMemoryPriceTrackingPlatformService()
    object_id = service.create("user1", "payload1")
    
    service.mutate(object_id, "payload2", "idem1")
    service.mutate(object_id, "payload3", "idem1") # Ignored
    
    result = service.get_by_id(object_id)
    assert result == "payload2"

def test_get_non_existent():
    service: PriceTrackingPlatformService = InMemoryPriceTrackingPlatformService()
    result = service.get_by_id("nonexistent")
    assert result is None
