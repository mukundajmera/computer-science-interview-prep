import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'v2_extended')))
import pytest
import time
from social_graph_engine_tao_v2 import (
    ObjectNode, Association, DatabaseV2, LeaderCacheV2, FollowerCacheV2, GraphEngineV2,
)


def make_stack():
    db = DatabaseV2()
    leader = LeaderCacheV2(db)
    follower = FollowerCacheV2(leader)
    engine = GraphEngineV2(db, leader, follower)
    return db, leader, follower, engine


# ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

def test_object_crud():
    db = DatabaseV2()
    obj = ObjectNode(1, 1, "User A")
    db.add_object(obj)

    assert db.get_object(1).data == "User A"
    db.update_object(1, "User A Updated")
    assert db.get_object(1).data == "User A Updated"

    db.delete_object(1)
    assert db.get_object(1) is None


def test_association_crud_and_follower_cache():
    db, leader, follower, engine = make_stack()

    assoc = Association(id1=1, atype=1, id2=2, timestamp=int(time.time()), data="")
    follower.add_association(assoc)

    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 2

    assoc2 = Association(id1=1, atype=1, id2=3, timestamp=int(time.time()), data="")
    follower.add_association(assoc2)

    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 2

    follower.delete_association(1, 1, 2)
    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 3


def test_invalidation_bus():
    db = DatabaseV2()
    leader = LeaderCacheV2(db)
    f1 = FollowerCacheV2(leader)
    f2 = FollowerCacheV2(leader)

    f1.get_associations(1, 1)
    assert (1, 1) in f1.cache

    assoc = Association(id1=1, atype=1, id2=2, timestamp=int(time.time()), data="")
    f2.add_association(assoc)

    assert (1, 1) not in f1.cache

    assocs = f1.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 2


def test_mutual_friends():
    db, leader, follower, engine = make_stack()

    follower.add_association(Association(1, 1, 3, 1, ""))
    follower.add_association(Association(1, 1, 4, 1, ""))
    follower.add_association(Association(1, 1, 5, 1, ""))

    follower.add_association(Association(2, 1, 4, 1, ""))
    follower.add_association(Association(2, 1, 5, 1, ""))
    follower.add_association(Association(2, 1, 6, 1, ""))

    mutuals = engine.get_mutual_friends(1, 2, 1)
    assert set(mutuals) == {4, 5}


def test_supernode_virtual_sharding():
    db, leader, follower, engine = make_stack()

    supernode_id = 1000
    for i in range(20):
        follower.add_association(Association(supernode_id, 1, i, i, ""))

    assocs = follower.get_associations(supernode_id, 1)
    assert len(assocs) == 20

    buckets_used = set()
    for key in db.associations.keys():
        id1, atype, bucket_id = key
        if id1 == supernode_id:
            buckets_used.add(bucket_id)

    assert len(buckets_used) > 1


def test_assoc_range_get_count():
    db, leader, follower, engine = make_stack()

    base_time = 1000
    follower.add_association(Association(1, 1, 2, base_time, ""))
    follower.add_association(Association(1, 1, 3, base_time + 10, ""))
    follower.add_association(Association(1, 1, 4, base_time + 20, ""))

    assert follower.assoc_count(1, 1) == 3

    range_res = follower.assoc_range(1, 1, base_time + 5, base_time + 25)
    assert len(range_res) == 2
    assert any(a.id2 == 3 for a in range_res)
    assert any(a.id2 == 4 for a in range_res)

    get_res = follower.assoc_get(1, 1, {2, 4})
    assert len(get_res) == 2
    assert any(a.id2 == 2 for a in get_res)
    assert any(a.id2 == 4 for a in get_res)


# ---------- v2 improvement 1: cursor-based pagination (FOLLOW-UPS.md #1) ----------

def test_cursor_pagination_walks_full_list_once_in_order():
    db, leader, follower, engine = make_stack()
    # 20 edges with distinct, increasing timestamps.
    for i in range(20):
        follower.add_association(Association(1, 1, 100 + i, 1000 + i, ""))

    seen = []
    cursor = None
    pages = 0
    while True:
        page, cursor = engine.assoc_page(1, 1, 6, cursor)
        seen.extend(a.id2 for a in page)
        pages += 1
        if cursor is None:
            break

    # Pages of 6, 6, 6, 2; newest first; no duplicates, none lost.
    assert pages == 4
    assert len(seen) == 20
    assert len(set(seen)) == 20
    assert seen == sorted(seen, reverse=True)


def test_cursor_pagination_tie_breaks_on_id2():
    db, leader, follower, engine = make_stack()
    # Same timestamp on every edge forces the id2 tie-break in the cursor.
    for id2 in [5, 3, 9, 7]:
        follower.add_association(Association(1, 1, id2, 1000, ""))

    first, cursor = engine.assoc_page(1, 1, 2)
    assert [a.id2 for a in first] == [9, 7]

    second, cursor = engine.assoc_page(1, 1, 2, cursor)
    assert [a.id2 for a in second] == [5, 3]
    assert cursor is None


def test_cursor_pagination_empty_for_unknown_list():
    db, leader, follower, engine = make_stack()
    page, cursor = engine.assoc_page(42, 1, 5)
    assert page == []
    assert cursor is None


# ---------- v2 improvement 2: read-your-writes versioning (FOLLOW-UPS.md #2) ----------

def test_versions_bump_on_every_write():
    db, leader, follower, engine = make_stack()

    v1 = follower.add_association(Association(1, 1, 2, 1000, ""))
    v2 = follower.add_association(Association(1, 1, 3, 1001, ""))
    v3 = follower.delete_association(1, 1, 2)

    assert v1 == 1
    assert v2 == 2
    assert v3 == 3
    assert leader.get_version(1, 1) == 3


def test_read_your_writes_survives_invalidation_bus_lag():
    db = DatabaseV2()
    leader = LeaderCacheV2(db)
    writer = FollowerCacheV2(leader)
    lagging = FollowerCacheV2(leader)

    writer.add_association(Association(1, 1, 2, 1000, ""))
    lagging.get_associations(1, 1)  # pull the v1 list into the lagging region

    # Wormhole goes down for the lagging region, then a write lands: the
    # invalidation message never reaches it.
    lagging.set_bus_connected(False)
    new_version = writer.add_association(Association(1, 1, 3, 1001, ""))
    assert new_version == 2

    # A plain read serves the stale entry.
    stale = lagging.get_associations(1, 1)
    assert len(stale) == 1

    # The client stored the write's version; sending it as min_version
    # force-bypasses the stale cache entry (FOLLOW-UPS.md #2).
    fresh = lagging.get_associations(1, 1, min_version=new_version)
    assert len(fresh) == 2
    assert {a.id2 for a in fresh} == {2, 3}


# ---------- v2 improvement 3: inverse edge writes (FOLLOW-UPS.md variants #1) ----------

def test_inverse_edges_serve_both_directions():
    db, leader, follower, engine = make_stack()
    FOLLOWS, FOLLOWED_BY = 1, 2

    engine.add_inverse_association(1, FOLLOWS, 2, FOLLOWED_BY, 1000)
    engine.add_inverse_association(3, FOLLOWS, 2, FOLLOWED_BY, 1001)

    following = follower.get_associations(1, FOLLOWS)
    assert [a.id2 for a in following] == [2]

    followers_of_2 = follower.get_associations(2, FOLLOWED_BY)
    assert {a.id2 for a in followers_of_2} == {1, 3}


def test_inverse_delete_removes_both_directions():
    db, leader, follower, engine = make_stack()
    FOLLOWS, FOLLOWED_BY = 1, 2

    engine.add_inverse_association(1, FOLLOWS, 2, FOLLOWED_BY, 1000)
    assert follower.assoc_count(2, FOLLOWED_BY) == 1

    engine.delete_inverse_association(1, FOLLOWS, 2, FOLLOWED_BY)
    assert follower.assoc_count(1, FOLLOWS) == 0
    assert follower.assoc_count(2, FOLLOWED_BY) == 0
