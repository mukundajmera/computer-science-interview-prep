import pytest
import sys
import os

# Dynamic path to load v1-basic module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from autocomplete_service import SearchAutocompleteService

@pytest.fixture
def profanity_blacklist():
    return {"badword", "profane"}

def test_suggestions_ordering(profanity_blacklist):
    service = SearchAutocompleteService(profanity_blacklist)
    
    # Adding queries multiple times to simulate frequency
    for _ in range(3):
        service.add_query_log("apple")
        
    for _ in range(4):
        service.add_query_log("app")
        
    for _ in range(2):
        service.add_query_log("application")
        
    service.add_query_log("append")
    service.add_query_log("appreciate")
    service.add_query_log("apply")
    service.add_query_log("apt")
    
    service.rebuild_trie()
    
    suggestions = service.get_suggestions("app")
    
    # Top 5 should be returned. Frequencies: 
    # app: 4, apple: 3, application: 2, append: 1, appreciate: 1, apply: 1
    assert len(suggestions) == 5
    assert suggestions[0] == "app"
    assert suggestions[1] == "apple"
    assert suggestions[2] == "application"

def test_prefix_limit(profanity_blacklist):
    service = SearchAutocompleteService(profanity_blacklist)
    
    very_long_query = "a" * 60
    for _ in range(10):
        service.add_query_log(very_long_query)
        
    service.rebuild_trie()
    
    long_prefix = "a" * 50
    suggestions = service.get_suggestions(long_prefix)
    assert len(suggestions) == 1
    assert suggestions[0] == very_long_query
    
    capped_prefix = "a" * 70
    capped_suggestions = service.get_suggestions(capped_prefix)
    assert len(capped_suggestions) == 1
    assert capped_suggestions[0] == very_long_query

def test_blacklist_filtering(profanity_blacklist):
    service = SearchAutocompleteService(profanity_blacklist)
    
    for _ in range(10):
        service.add_query_log("goodword")
        
    for _ in range(20):
        service.add_query_log("badword")
        
    for _ in range(15):
        service.add_query_log("proper language")
        
    for _ in range(5):
        service.add_query_log("profane language")
        
    service.rebuild_trie()
    
    pro_suggestions = service.get_suggestions("pro")
    assert len(pro_suggestions) == 1
    assert pro_suggestions[0] == "proper language"
    
    bad_suggestions = service.get_suggestions("bad")
    assert len(bad_suggestions) == 0

def test_rebuild_from_aggregated_frequencies(profanity_blacklist):
    service = SearchAutocompleteService(profanity_blacklist)
    
    service.add_query_log("test")
    service.rebuild_trie()
    
    assert service.get_suggestions("te") == ["test"]
    
    for _ in range(2):
        service.add_query_log("tester")
    
    service.rebuild_trie()
    
    suggestions = service.get_suggestions("te")
    assert len(suggestions) == 2
    assert suggestions[0] == "tester"
    assert suggestions[1] == "test"

def test_case_insensitivity(profanity_blacklist):
    service = SearchAutocompleteService(profanity_blacklist)
    
    service.add_query_log("HELLO")
    service.add_query_log("Hello World")
    
    service.rebuild_trie()
    
    assert "hello" in service.get_suggestions("HELL")
    assert "hello world" in service.get_suggestions("hel")
    assert "hello" in service.get_suggestions("He")
