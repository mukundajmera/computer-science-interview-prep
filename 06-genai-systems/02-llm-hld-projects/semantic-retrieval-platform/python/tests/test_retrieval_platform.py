import os
import sys

# Ensure v1-basic is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

import pytest
from retrieval_platform import RetrievalPipeline, DocumentChunk, RetrievalResult, EmbeddingService, cosine_similarity

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-6
    assert abs(cosine_similarity(v1, v3) - 0.0) < 1e-6

def test_vector_store_operations():
    pipeline = RetrievalPipeline()
    tenant_id = "tenant-a"

    pipeline.ingest(tenant_id, "how do we rotate api keys?", {"source": "doc1"}, ["eng", "admin"])
    pipeline.ingest(tenant_id, "the quick brown fox jumps", {"source": "doc2"}, ["eng"])
    pipeline.ingest("tenant-b", "this should not be retrieved", {"source": "doc3"}, ["eng"])

    # Retrieve without reranking and cache to test vector store directly
    results = pipeline.retrieve(tenant_id, "api keys", top_k=2, acl_groups=["eng"], use_cache=False, do_rerank=False)

    assert len(results) > 0
    # doc1 should have higher score for 'api keys' than doc2
    doc1_found = False
    for res in results:
        if "api keys" in res.text:
            doc1_found = True
            break
    assert doc1_found

def test_retrieval_with_acl_filtering():
    pipeline = RetrievalPipeline()
    tenant_id = "tenant-a"

    pipeline.ingest(tenant_id, "secret password to production", {"source": "secrets"}, ["admin"])
    pipeline.ingest(tenant_id, "how to change your password", {"source": "help"}, ["eng", "admin", "user"])

    # "user" shouldn't see "secret password to production"
    user_results = pipeline.retrieve(tenant_id, "password", top_k=5, acl_groups=["user"], use_cache=False, do_rerank=False)
    assert len(user_results) == 1
    assert "change your password" in user_results[0].text

    # "admin" should see both
    admin_results = pipeline.retrieve(tenant_id, "password", top_k=5, acl_groups=["admin"], use_cache=False, do_rerank=False)
    assert len(admin_results) == 2

def test_query_expansion():
    pipeline = RetrievalPipeline()
    tenant_id = "tenant-a"

    pipeline.ingest(tenant_id, "how to update interface keys", {"source": "doc1"}, ["eng"])
    pipeline.ingest(tenant_id, "random text without keywords", {"source": "doc2"}, ["eng"])

    # "rotate api" should expand to include "update" and "interface"
    results = pipeline.retrieve(tenant_id, "rotate api keys", top_k=1, acl_groups=["eng"], use_cache=False, do_rerank=False)

    assert len(results) == 1
    assert "update interface keys" in results[0].text

def test_semantic_caching():
    pipeline = RetrievalPipeline()
    tenant_id = "tenant-a"

    pipeline.ingest(tenant_id, "some text about caching", {"source": "doc1"}, ["eng"])

    # First request
    results1 = pipeline.retrieve(tenant_id, "caching details", top_k=1, acl_groups=["eng"], use_cache=True, do_rerank=True)
    assert len(results1) == 1

    # Second request with exact same query should hit cache. We can test this by changing the store
    # and ensuring we still get the old result.
    # To mock a change, we'll clear the vector store.
    pipeline.vector_store.data = {}

    results2 = pipeline.retrieve(tenant_id, "caching details", top_k=1, acl_groups=["eng"], use_cache=True, do_rerank=True)
    assert len(results2) == 1
    assert results1[0].chunk_id == results2[0].chunk_id

def test_reranking():
    pipeline = RetrievalPipeline()
    tenant_id = "tenant-a"

    # Ingest docs that might have similar base embeddings due to dummy embedding logic
    pipeline.ingest(tenant_id, "rotate api keys for production", {"source": "doc1"}, ["eng"])
    pipeline.ingest(tenant_id, "keys api rotate", {"source": "doc2"}, ["eng"])

    # A query that exactly overlaps with doc1
    results = pipeline.retrieve(tenant_id, "rotate api keys for production", top_k=2, acl_groups=["eng"], use_cache=False, do_rerank=True)

    # Because of reranker exact word overlap bonus, doc1 should be scored higher
    assert len(results) == 2
    assert results[0].text == "rotate api keys for production"
