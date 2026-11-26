import sys
import os
import time
from typing import List
import uuid

# Insert base directory into path for dynamic imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_price_tracking_platform_service import DistributedPriceTrackingPlatformService, DistributedIdempotencyStore

class InMemoryDistributedIdempotencyStore:
    def __init__(self):
        self.claims = {}

    def claim(self, key: str, ttl_ms: int) -> bool:
        now = time.time() * 1000
        if key in self.claims and self.claims[key] > now:
            return False # Already claimed and not expired
        self.claims[key] = now + ttl_ms
        return True

class InMemoryDistributedPriceTrackingPlatformService:
    def __init__(self, idempotency_store: DistributedIdempotencyStore):
        self.idempotency_store = idempotency_store
        self.regional_data = {} # region -> (id -> payload)
        self.regional_views = {} # region -> list of payloads

    def create(self, owner_id: str, payload: str, region: str) -> str:
        object_id = str(uuid.uuid4())
        
        if region not in self.regional_data:
            self.regional_data[region] = {}
        if region not in self.regional_views:
            self.regional_views[region] = []
            
        self.regional_data[region][object_id] = payload
        self.regional_views[region].insert(0, payload)
        
        return object_id

    def mutate_with_replay_token(self, object_id: str, mutation_payload: str, idempotency_key: str, replay_token: str) -> None:
        if not self.idempotency_store.claim(idempotency_key, 60000):
            return # Duplicate
            
        # For testing, update all regions that have this id
        for region, data in self.regional_data.items():
            if object_id in data:
                data[object_id] = mutation_payload
                self.regional_views[region].insert(0, mutation_payload) # Append to view

    def read_region_view(self, region: str, limit: int) -> List[str]:
        return self.regional_views.get(region, [])[:limit]

def test_create_and_read_region_view():
    store = InMemoryDistributedIdempotencyStore()
    service: DistributedPriceTrackingPlatformService = InMemoryDistributedPriceTrackingPlatformService(store)
    
    service.create("user1", "payload-us-1", "us-east")
    service.create("user2", "payload-eu-1", "eu-west")
    service.create("user1", "payload-us-2", "us-east")
    
    us_view = service.read_region_view("us-east", 5)
    assert len(us_view) == 2
    assert us_view[0] == "payload-us-2"
    
    eu_view = service.read_region_view("eu-west", 5)
    assert len(eu_view) == 1
    assert eu_view[0] == "payload-eu-1"

def test_mutate_with_replay_token():
    store = InMemoryDistributedIdempotencyStore()
    service: DistributedPriceTrackingPlatformService = InMemoryDistributedPriceTrackingPlatformService(store)
    
    object_id = service.create("user1", "payload1", "us-east")
    service.mutate_with_replay_token(object_id, "payload1-mutated", "idem1", "token1")
    
    us_view = service.read_region_view("us-east", 1)
    assert len(us_view) == 1
    assert us_view[0] == "payload1-mutated"

def test_mutate_with_replay_token_idempotency():
    store = InMemoryDistributedIdempotencyStore()
    service: DistributedPriceTrackingPlatformService = InMemoryDistributedPriceTrackingPlatformService(store)
    
    object_id = service.create("user1", "payload1", "us-east")
    service.mutate_with_replay_token(object_id, "payload1-mutated", "idem1", "token1")
    service.mutate_with_replay_token(object_id, "payload1-mutated-again", "idem1", "token2") # Ignored
    
    us_view = service.read_region_view("us-east", 2)
    assert us_view[0] == "payload1-mutated"
