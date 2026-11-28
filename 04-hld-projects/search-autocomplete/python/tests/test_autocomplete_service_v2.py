import pytest
import sys
import os

# Dynamic path to load v2-extended module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from autocomplete_service_v2 import (
    PrefixShardRouterV2,
    SearchAutocompleteServiceV2,
)

# Fixed timestamps keep the sliding-window math deterministic.
# bucket_seconds=60, window_buckets=5 -> window covers buckets
# (now//60 - 4) .. (now//60). ts=0 is bucket 0; ts=1000 is bucket 16;
# ts=1301 is bucket 21, whose window starts at bucket 17.
T_OLD = 0
T_NOW = 1000
T_EXPIRED = 1301


@pytest.fixture
def profanity_blacklist():
    return {"badword", "profane"}


# ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

def test_suggestions_ordering(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist)

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

    assert len(suggestions) == 5
    assert suggestions[0] == "app"
    assert suggestions[1] == "apple"
    assert suggestions[2] == "application"


def test_prefix_limit(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist)

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
    service = SearchAutocompleteServiceV2(profanity_blacklist)

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
    service = SearchAutocompleteServiceV2(profanity_blacklist)

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
    service = SearchAutocompleteServiceV2(profanity_blacklist)

    service.add_query_log("HELLO")
    service.add_query_log("Hello World")

    service.rebuild_trie()

    assert "hello" in service.get_suggestions("HELL")
    assert "hello world" in service.get_suggestions("hel")
    assert "hello" in service.get_suggestions("He")


# ---------- v2 improvement 1: trending fast-path (FOLLOW-UPS.md #1) ----------

def test_trending_query_overtakes_batch_leader(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist, trending_weight=50)

    for _ in range(20):
        service.add_query_log("apple", timestamp=T_OLD)
    for _ in range(5):
        service.add_query_log("applestore", timestamp=T_OLD)
    for _ in range(3):
        service.add_query_log("applestore", timestamp=T_NOW)

    service.rebuild_trie()

    # Batch view: apple 20 beats applestore 8.
    plain = service.get_suggestions("app")
    assert plain[0] == "apple"

    # Blended at T_NOW: apple = 20 + 50*0 = 20;
    # applestore = 8 + 50*3 = 158 -> trending spike wins.
    blended = service.get_blended_suggestions("app", timestamp=T_NOW)
    assert blended[0] == "applestore"
    assert blended[1] == "apple"


def test_trending_window_expires_old_queries(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist, trending_weight=50)

    for _ in range(10):
        service.add_query_log("zoo", timestamp=T_OLD)
    for _ in range(3):
        service.add_query_log("zoom call", timestamp=T_NOW)

    service.rebuild_trie()

    # Inside the window: zoom call = 3 + 50*3 = 153 beats zoo = 10.
    spiking = service.get_blended_suggestions("zo", timestamp=T_NOW)
    assert spiking[0] == "zoom call"

    # One bucket past the window: recent count is 0, batch order returns.
    settled = service.get_blended_suggestions("zo", timestamp=T_EXPIRED)
    assert settled[0] == "zoo"


def test_blended_matches_plain_when_nothing_trending(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist)

    for _ in range(3):
        service.add_query_log("apple", timestamp=T_OLD)
    for _ in range(4):
        service.add_query_log("app", timestamp=T_OLD)
    for _ in range(2):
        service.add_query_log("application", timestamp=T_OLD)

    service.rebuild_trie()

    # All counts are far outside the window, so blending changes nothing.
    assert service.get_blended_suggestions("app", timestamp=T_EXPIRED) == \
        service.get_suggestions("app")


def test_trending_candidates_skip_profanity(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist)
    # Bypass the add-time filter to prove the read-time defense holds.
    service.aggregator.add_query("badword deals", timestamp=T_NOW)

    service.rebuild_trie()

    assert service.get_blended_suggestions("bad", timestamp=T_NOW) == []


# ---------- v2 improvement 2: personalized autocomplete (FOLLOW-UPS variants) ----------

def test_personal_history_boosts_own_queries(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist, personal_weight=10)

    for _ in range(20):
        service.add_query_log("apple", timestamp=T_OLD)
    for _ in range(3):
        service.record_user_query("u1", "apple pie", timestamp=T_OLD)

    service.rebuild_trie()

    # For u1: apple pie = 3 + 10*3 = 33 beats apple = 20.
    blended = service.get_blended_suggestions("app", timestamp=T_EXPIRED, user_id="u1")
    assert blended[0] == "apple pie"


def test_personal_boost_not_shared_between_users(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist, personal_weight=10)

    for _ in range(20):
        service.add_query_log("apple", timestamp=T_OLD)
    for _ in range(3):
        service.record_user_query("u1", "apple pie", timestamp=T_OLD)

    service.rebuild_trie()

    # u2 gets no personal boost: apple pie = 3 + 10*0 = 3 loses to apple = 20.
    blended = service.get_blended_suggestions("app", timestamp=T_EXPIRED, user_id="u2")
    assert blended[0] == "apple"


def test_user_history_evicts_oldest_beyond_cap(profanity_blacklist):
    service = SearchAutocompleteServiceV2(profanity_blacklist, max_user_queries=3)

    for query in ["xa", "xb", "xc", "xd"]:
        service.record_user_query("u1", query, timestamp=T_OLD)

    service.rebuild_trie()

    # "xa" was evicted, so it scores batch-only (1) while the capped
    # history still boosts xb/xc/xd to 1 + 10 = 11 each (lexicographic tie).
    blended = service.get_blended_suggestions("x", timestamp=T_EXPIRED, user_id="u1")
    assert blended == ["xb", "xc", "xd", "xa"]


# ---------- v2 improvement 3: prefix-range sharding (FOLLOW-UPS.md #2) ----------

def test_shard_router_routes_and_serves(profanity_blacklist):
    router = PrefixShardRouterV2(profanity_blacklist=profanity_blacklist)

    router.add_query_log("apple", timestamp=T_OLD)
    router.add_query_log("mango", timestamp=T_OLD)
    router.rebuild_all()

    # Boundaries a,d,g,j,m,p,s,v,y: 'a' -> shard 0 (a-c), 'm' -> shard 4 (m-o).
    assert router.shard_index("apple") == 0
    assert router.shard_index("mango") == 4

    assert router.get_suggestions("app") == ["apple"]
    assert router.get_suggestions("man") == ["mango"]
    # Each shard only holds its own range's queries.
    assert router.shards[0].get_suggestions("man") == []


def test_shard_router_catch_all_and_empty_prefix(profanity_blacklist):
    router = PrefixShardRouterV2(profanity_blacklist=profanity_blacklist)

    # Non-letter prefixes land on the catch-all (last) shard.
    assert router.shard_index("123abc") == len(router.boundaries) - 1
    router.add_query_log("123abc", timestamp=T_OLD)
    router.rebuild_all()
    assert router.get_suggestions("123") == ["123abc"]

    # Empty prefix is a no-op everywhere.
    assert router.shard_index("") is None
    router.add_query_log("", timestamp=T_OLD)
    assert router.get_suggestions("") == []
    assert router.get_blended_suggestions("", timestamp=T_NOW) == []
