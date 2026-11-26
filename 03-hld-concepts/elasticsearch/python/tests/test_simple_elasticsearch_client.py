import sys
import os

# Add v1-simple to sys.path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_elasticsearch_client import SimpleElasticsearchClient, Document

def test_search_text_matches_title_and_body():
    client = SimpleElasticsearchClient()
    client.index(Document("1", "Search Engine Basics", "Intro to inverted indexes", {"search"}))
    client.index(Document("2", "Advanced Topics", "More search capabilities", {"search"}))
    client.index(Document("3", "Databases", "Relational db guide", set()))

    results1 = client.search_text("search")
    assert len(results1) == 2, "Should find 'search' in title or body"

    results2 = client.search_text("inverted")
    assert len(results2) == 1, "Should find 'inverted' in body"
    assert results2[0].id == "1"

def test_filter_by_tag():
    client = SimpleElasticsearchClient()
    client.index(Document("1", "Redis", "Cache", {"cache"}))
    client.index(Document("2", "Elasticsearch", "Search", {"search", "distributed"}))
    client.index(Document("3", "Solr", "Search", {"search", "distributed"}))

    results = client.filter_by_tag("search")
    assert len(results) == 2, "Should find 2 documents with 'search' tag"

    cache_results = client.filter_by_tag("cache")
    assert len(cache_results) == 1, "Should find 1 document with 'cache' tag"

def test_search_returns_empty_when_no_match():
    client = SimpleElasticsearchClient()
    client.index(Document("1", "Title", "Body", set()))

    text_results = client.search_text("MissingWord")
    assert len(text_results) == 0, "Text search should return empty when no match"

    tag_results = client.filter_by_tag("missing_tag")
    assert len(tag_results) == 0, "Tag filter should return empty when no match"
