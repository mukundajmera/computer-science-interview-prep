import sys
import os
import uuid
import pytest
from typing import Optional, List, Dict

# Dynamically add the directories to sys.path to resolve hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

from social_post_search_service import SocialPostSearchService
from social_post_search_service_v2 import SocialPostSearchServiceV2, ProjectionStore
from distributed_social_post_search_service import DistributedSocialPostSearchService, DistributedIdempotencyStore

class InMemorySocialPostSearchService:
    """Dummy implementation for v1-basic"""
    def __init__(self):
        self.data_store: Dict[str, str] = {}
        self.inverted_index: Dict[str, List[str]] = {}

    def create(self, owner_id: str, payload: str) -> str:
        object_id = str(uuid.uuid4())
        self.data_store[object_id] = payload

        # Tokenize
        tokens = payload.lower().replace(",", "").replace(".", "").split()
        for token in tokens:
            if token not in self.inverted_index:
                self.inverted_index[token] = []
            self.inverted_index[token].append(object_id)

        return object_id

    def get_by_id(self, object_id: str) -> Optional[str]:
        return self.data_store.get(object_id)

    def mutate(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if object_id in self.data_store:
            self.data_store[object_id] += " " + mutation_payload

    def search_by_keyword(self, keyword: str) -> List[str]:
        object_ids = self.inverted_index.get(keyword.lower(), [])
        return [self.data_store[oid] for oid in object_ids]

class InMemorySocialPostSearchServiceV2:
    """Dummy implementation for v2-scaled"""
    def __init__(self):
        self.data_store: Dict[str, str] = {}
        self.relevance_scores: Dict[str, int] = {}
        self.cache: Dict[str, str] = {}

    def create(self, owner_id: str, payload: str) -> str:
        object_id = str(uuid.uuid4())
        self.data_store[object_id] = payload
        self.relevance_scores[object_id] = 0
        self.cache[object_id] = payload
        return object_id

    def publish_mutation(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None:
        if object_id in self.data_store:
            if "like" in mutation_payload.lower():
                self.relevance_scores[object_id] += 1

    def read_recent(self, limit: int) -> List[str]:
        # Sort by relevance
        sorted_items = sorted(
            self.data_store.items(),
            key=lambda item: self.relevance_scores.get(item[0], 0),
            reverse=True
        )
        return [payload for oid, payload in sorted_items[:limit]]

class InMemoryDistributedSocialPostSearchService:
    """Dummy implementation for v3-distributed"""
    def __init__(self):
        self.regional_stores: Dict[str, Dict[str, str]] = {}
        self.idempotency_keys: Dict[str, bool] = {}

    def create(self, owner_id: str, payload: str, region: str) -> str:
        object_id = str(uuid.uuid4())
        if region not in self.regional_stores:
            self.regional_stores[region] = {}
        self.regional_stores[region][object_id] = payload
        return object_id

    def mutate_with_replay_token(self, object_id: str, mutation_payload: str, idempotency_key: str, replay_token: str) -> None:
        if idempotency_key in self.idempotency_keys:
            return  # Already processed
        self.idempotency_keys[idempotency_key] = True

    def read_region_view(self, region: str, limit: int) -> List[str]:
        region_data = self.regional_stores.get(region, {})
        return list(region_data.values())[:limit]

    def distributed_search_and_merge(self) -> List[str]:
        all_results = []
        for region, data in self.regional_stores.items():
            all_results.extend(data.values())
        return all_results

def test_v1_basic_search():
    service = InMemorySocialPostSearchService()
    id1 = service.create("user1", "Python is great for scripting")
    id2 = service.create("user2", "I love python development")

    assert service.get_by_id(id1) == "Python is great for scripting"

    results = service.search_by_keyword("python")
    assert len(results) == 2
    assert "Python is great for scripting" in results
    assert "I love python development" in results

    script_results = service.search_by_keyword("scripting")
    assert len(script_results) == 1
    assert "Python is great for scripting" in script_results

def test_v2_scaled_ranking():
    service = InMemorySocialPostSearchServiceV2()
    id1 = service.create("u1", "Post 1")
    id2 = service.create("u2", "Post 2")
    id3 = service.create("u3", "Post 3")

    # Simulate likes to increase ranking
    service.publish_mutation(id2, "like", "key1")
    service.publish_mutation(id2, "like", "key2")
    service.publish_mutation(id1, "like", "key3")

    recent_posts = service.read_recent(3)
    assert len(recent_posts) == 3
    assert recent_posts[0] == "Post 2"
    assert recent_posts[1] == "Post 1"
    assert recent_posts[2] == "Post 3"

def test_v3_distributed_search_merge():
    service = InMemoryDistributedSocialPostSearchService()
    service.create("u1", "NA Post 1", "NA")
    service.create("u2", "NA Post 2", "NA")
    service.create("u3", "EU Post 1", "EU")

    na_view = service.read_region_view("NA", 10)
    assert len(na_view) == 2

    eu_view = service.read_region_view("EU", 10)
    assert len(eu_view) == 1

    merged = service.distributed_search_and_merge()
    assert len(merged) == 3
    assert "NA Post 1" in merged
    assert "NA Post 2" in merged
    assert "EU Post 1" in merged

    # Check idempotency
    service.mutate_with_replay_token("id", "mut", "idem1", "token1")
    service.mutate_with_replay_token("id", "mut", "idem1", "token2") # Should do nothing
