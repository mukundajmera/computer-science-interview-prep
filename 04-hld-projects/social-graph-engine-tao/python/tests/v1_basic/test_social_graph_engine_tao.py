import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'v1_basic')))
import pytest
import time
from social_graph_engine_tao import ObjectNode, Association, Database, LeaderCache, FollowerCache, GraphEngine

def test_object_crud():
    db = Database()
    obj = ObjectNode(1, 1, "User A")
    db.add_object(obj)
    
    assert db.get_object(1).data == "User A"
    db.update_object(1, "User A Updated")
    assert db.get_object(1).data == "User A Updated"
    
    db.delete_object(1)
    assert db.get_object(1) is None

def test_association_crud_and_follower_cache():
    db = Database()
    leader = LeaderCache(db)
    follower = FollowerCache(leader)
    engine = GraphEngine(db, leader, follower)
    
    # Add an association
    assoc = Association(id1=1, atype=1, id2=2, timestamp=int(time.time()), data="")
    follower.add_association(assoc)
    
    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 2
    
    # Add another association
    assoc2 = Association(id1=1, atype=1, id2=3, timestamp=int(time.time()), data="")
    follower.add_association(assoc2)
    
    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 2
    
    follower.delete_association(1, 1, 2)
    assocs = follower.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 3

def test_invalidation_bus():
    db = Database()
    leader = LeaderCache(db)
    f1 = FollowerCache(leader)
    f2 = FollowerCache(leader)
    
    # f1 reads, pulling into its cache
    f1.get_associations(1, 1)
    assert (1, 1) in f1.cache
    
    # f2 writes, changing db and leader cache, triggering broadcast
    assoc = Association(id1=1, atype=1, id2=2, timestamp=int(time.time()), data="")
    f2.add_association(assoc)
    
    # f1's cache should be invalidated
    assert (1, 1) not in f1.cache
    
    # Next read should miss f1's cache and pull from leader
    assocs = f1.get_associations(1, 1)
    assert len(assocs) == 1
    assert assocs[0].id2 == 2

def test_mutual_friends():
    db = Database()
    leader = LeaderCache(db)
    follower = FollowerCache(leader)
    engine = GraphEngine(db, leader, follower)
    
    # User 1 friends: 3, 4, 5
    follower.add_association(Association(1, 1, 3, 1, ""))
    follower.add_association(Association(1, 1, 4, 1, ""))
    follower.add_association(Association(1, 1, 5, 1, ""))
    
    # User 2 friends: 4, 5, 6
    follower.add_association(Association(2, 1, 4, 1, ""))
    follower.add_association(Association(2, 1, 5, 1, ""))
    follower.add_association(Association(2, 1, 6, 1, ""))
    
    mutuals = engine.get_mutual_friends(1, 2, 1)
    assert set(mutuals) == {4, 5}

def test_supernode_virtual_sharding():
    db = Database()
    leader = LeaderCache(db)
    follower = FollowerCache(leader)
    
    supernode_id = 1000
    for i in range(20):
        follower.add_association(Association(supernode_id, 1, i, i, ""))
    
    assocs = follower.get_associations(supernode_id, 1)
    assert len(assocs) == 20
    
    # Check that they are stored in multiple buckets in the db
    buckets_used = set()
    for key in db.associations.keys():
        id1, atype, bucket_id = key
        if id1 == supernode_id:
            buckets_used.add(bucket_id)
    
    # With 20 associations and 10 buckets, some should end up in different buckets
    assert len(buckets_used) > 1



def test_assoc_range_get_count():
    db = Database()
    leader = LeaderCache(db)
    follower = FollowerCache(leader)
    
    base_time = 1000
    follower.add_association(Association(1, 1, 2, base_time, ""))
    follower.add_association(Association(1, 1, 3, base_time + 10, ""))
    follower.add_association(Association(1, 1, 4, base_time + 20, ""))
    
    # count
    assert follower.assoc_count(1, 1) == 3
    
    # range
    range_res = follower.assoc_range(1, 1, base_time + 5, base_time + 25)
    assert len(range_res) == 2
    assert any(a.id2 == 3 for a in range_res)
    assert any(a.id2 == 4 for a in range_res)
    
    # get
    get_res = follower.assoc_get(1, 1, {2, 4})
    assert len(get_res) == 2
    assert any(a.id2 == 2 for a in get_res)
    assert any(a.id2 == 4 for a in get_res)
