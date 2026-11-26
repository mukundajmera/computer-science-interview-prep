import sys
import os
import pytest
from typing import Optional, List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-scaled'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-distributed'))

from auction_platform_service import AuctionPlatformService
from auction_platform_service_v2 import AuctionPlatformServiceV2, ProjectionStore
from distributed_auction_platform_service import DistributedAuctionPlatformService, DistributedIdempotencyStore

class InMemoryAuctionPlatformV1:
    def __init__(self):
        self.items: Dict[str, Dict] = {}
        self.next_id = 1
        self.mutations = []

    def create(self, owner_id: str, payload: str) -> str:
        item_id = str(self.next_id)
        self.next_id += 1
        self.items[item_id] = {"owner": owner_id, "payload": payload}
        return item_id

    def get_by_id(self, object_id: str) -> Optional[str]:
        item = self.items.get(object_id)
        return item["payload"] if item else None

    def mutate(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if object_id in self.items:
            # We just track mutations for verification
            self.mutations.append((object_id, mutation_payload, idempotency_key))


class InMemoryProjectionStore:
    def __init__(self):
        self.projections: Dict[str, str] = {}
        self.recent_ids: List[str] = []

    def upsert_projection(self, object_id: str, snapshot: str) -> None:
        self.projections[object_id] = snapshot
        if object_id not in self.recent_ids:
            self.recent_ids.append(object_id)
        else:
            self.recent_ids.remove(object_id)
            self.recent_ids.append(object_id)

    def recent(self, limit: int) -> List[str]:
        recent = self.recent_ids[-limit:] if limit > 0 else []
        return [self.projections[r] for r in reversed(recent)]


class InMemoryAuctionPlatformV2:
    def __init__(self, projection_store: ProjectionStore):
        self.projection_store = projection_store
        self.next_id = 1
        self.events = []

    def create(self, owner_id: str, payload: str) -> str:
        item_id = str(self.next_id)
        self.next_id += 1
        self.projection_store.upsert_projection(item_id, payload)
        return item_id

    def publish_mutation(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        self.events.append((object_id, mutation_payload, idempotency_key))
        # Simple simulation: just update projection with mutation payload
        self.projection_store.upsert_projection(object_id, mutation_payload)

    def read_recent(self, limit: int) -> List[str]:
        return self.projection_store.recent(limit)


class InMemoryIdempotencyStore:
    def __init__(self):
        self.claimed: Dict[str, bool] = {}

    def claim(self, key: str, ttl_ms: int) -> bool:
        if key in self.claimed:
            return False
        self.claimed[key] = True
        return True


class InMemoryDistributedAuctionPlatform:
    def __init__(self, idempotency_store: DistributedIdempotencyStore):
        self.idempotency_store = idempotency_store
        self.items: Dict[str, Dict] = {}
        self.next_id = 1
        self.region_data: Dict[str, List[str]] = {}

    def create(self, owner_id: str, payload: str, region: str) -> str:
        item_id = str(self.next_id)
        self.next_id += 1
        self.items[item_id] = {"owner": owner_id, "payload": payload, "region": region}
        if region not in self.region_data:
            self.region_data[region] = []
        self.region_data[region].append(payload)
        return item_id

    def mutate_with_replay_token(self, object_id: str, mutation_payload: str, idempotency_key: str, replay_token: str) -> None:
        if self.idempotency_store.claim(idempotency_key, 1000):
            if object_id in self.items:
                region = self.items[object_id]["region"]
                self.items[object_id]["payload"] = mutation_payload
                self.region_data[region].append(mutation_payload)

    def read_region_view(self, region: str, limit: int) -> List[str]:
        if region in self.region_data:
            return list(reversed(self.region_data[region][-limit:]))
        return []


def test_v1_create_and_get():
    service: AuctionPlatformService = InMemoryAuctionPlatformV1()
    item_id = service.create("user1", "Item A")
    
    assert item_id == "1"
    assert service.get_by_id(item_id) == "Item A"
    assert service.get_by_id("999") is None


def test_v1_mutate():
    service: AuctionPlatformService = InMemoryAuctionPlatformV1()
    item_id = service.create("user1", "Item A")
    service.mutate(item_id, "Bid 100", "idem-1")
    
    assert len(service.mutations) == 1
    assert service.mutations[0] == (item_id, "Bid 100", "idem-1")


def test_v2_publish_and_read_recent():
    projection_store: ProjectionStore = InMemoryProjectionStore()
    service: AuctionPlatformServiceV2 = InMemoryAuctionPlatformV2(projection_store)
    
    id1 = service.create("user1", "Item A")
    id2 = service.create("user2", "Item B")
    
    recent = service.read_recent(2)
    assert len(recent) == 2
    assert recent[0] == "Item B"
    assert recent[1] == "Item A"
    
    service.publish_mutation(id1, "Item A - Bid 100", "idem-2")
    
    recent_after_mut = service.read_recent(2)
    assert recent_after_mut[0] == "Item A - Bid 100"
    assert recent_after_mut[1] == "Item B"


def test_v3_idempotent_mutation_and_region_view():
    idem_store: DistributedIdempotencyStore = InMemoryIdempotencyStore()
    service: DistributedAuctionPlatformService = InMemoryDistributedAuctionPlatform(idem_store)
    
    id1 = service.create("user1", "Item A", "US-EAST")
    id2 = service.create("user2", "Item B", "EU-WEST")
    
    service.mutate_with_replay_token(id1, "Item A - Bid 100", "idem-3", "token-1")
    service.mutate_with_replay_token(id1, "Item A - Bid 150", "idem-3", "token-2")  # Same key, should be ignored
    
    us_east_view = service.read_region_view("US-EAST", 5)
    # The view has original "Item A" and then "Item A - Bid 100".
    # Since we reverse the recent ones, index 0 is latest.
    assert len(us_east_view) == 2
    assert us_east_view[0] == "Item A - Bid 100"
    assert us_east_view[1] == "Item A"
    
    eu_west_view = service.read_region_view("EU-WEST", 5)
    assert len(eu_west_view) == 1
    assert eu_west_view[0] == "Item B"

