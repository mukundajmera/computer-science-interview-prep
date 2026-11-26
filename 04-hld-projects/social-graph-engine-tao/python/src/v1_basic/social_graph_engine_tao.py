import time
from typing import Dict, List, Optional, Tuple, Set

class ObjectNode:
    def __init__(self, id: int, otype: int, data: str):
        self.id = id
        self.otype = otype
        self.data = data

class Association:
    def __init__(self, id1: int, atype: int, id2: int, timestamp: int, data: str):
        self.id1 = id1
        self.atype = atype
        self.id2 = id2
        self.timestamp = timestamp
        self.data = data

class Database:
    def __init__(self):
        self.objects: Dict[int, ObjectNode] = {}
        # Sharding by id1, but using memory structures
        # For supernodes, we use virtual buckets.
        # Map from (id1, atype, bucket_id) -> List[Association]
        self.associations: Dict[Tuple[int, int, int], List[Association]] = {}

    def add_object(self, obj: ObjectNode):
        self.objects[obj.id] = obj

    def get_object(self, id: int) -> Optional[ObjectNode]:
        return self.objects.get(id)

    def update_object(self, id: int, data: str):
        if id in self.objects:
            self.objects[id].data = data

    def delete_object(self, id: int):
        if id in self.objects:
            del self.objects[id]

    def _get_bucket_id(self, id1: int, id2: int) -> int:
        if self._is_supernode(id1):
            return hash(id2) % 10 # 10 virtual buckets
        return 0

    def _is_supernode(self, id1: int) -> bool:
        # Mock condition for supernode
        return id1 >= 1000

    def add_association(self, assoc: Association):
        bucket_id = self._get_bucket_id(assoc.id1, assoc.id2)
        key = (assoc.id1, assoc.atype, bucket_id)
        if key not in self.associations:
            self.associations[key] = []
        self.associations[key].append(assoc)
        self.associations[key].sort(key=lambda x: x.timestamp, reverse=True)

    def delete_association(self, id1: int, atype: int, id2: int):
        bucket_id = self._get_bucket_id(id1, id2)
        key = (id1, atype, bucket_id)
        if key in self.associations:
            self.associations[key] = [a for a in self.associations[key] if a.id2 != id2]

    def get_associations(self, id1: int, atype: int) -> List[Association]:
        results = []
        if self._is_supernode(id1):
            for bucket_id in range(10):
                key = (id1, atype, bucket_id)
                results.extend(self.associations.get(key, []))
        else:
            key = (id1, atype, 0)
            results.extend(self.associations.get(key, []))
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]

class LeaderCache:
    def __init__(self, db: Database):
        self.db = db
        # Map from (id1, atype) to Association list
        self.cache: Dict[Tuple[int, int], List[Association]] = {}
        self.followers: List['FollowerCache'] = []
    
    def register_follower(self, follower: 'FollowerCache'):
        self.followers.append(follower)

    def broadcast_invalidation(self, id1: int, atype: int):
        for follower in self.followers:
            follower.invalidate(id1, atype)

    def add_association(self, assoc: Association):
        self.db.add_association(assoc)
        key = (assoc.id1, assoc.atype)
        if key in self.cache:
            # Check if association already exists in cache
            exists = any(a.id2 == assoc.id2 for a in self.cache[key])
            if not exists:
                self.cache[key].append(assoc)
                self.cache[key].sort(key=lambda x: x.timestamp, reverse=True)
        self.broadcast_invalidation(assoc.id1, assoc.atype)
        
    def delete_association(self, id1: int, atype: int, id2: int):
        self.db.delete_association(id1, atype, id2)
        key = (id1, atype)
        if key in self.cache:
            self.cache[key] = [a for a in self.cache[key] if a.id2 != id2]
        self.broadcast_invalidation(id1, atype)

    def get_associations(self, id1: int, atype: int) -> List[Association]:
        key = (id1, atype)
        if key not in self.cache:
            self.cache[key] = self.db.get_associations(id1, atype)
        return self.cache[key]

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]

class FollowerCache:
    def __init__(self, leader: LeaderCache):
        self.leader = leader
        self.cache: Dict[Tuple[int, int], List[Association]] = {}
        self.leader.register_follower(self)

    def invalidate(self, id1: int, atype: int):
        key = (id1, atype)
        if key in self.cache:
            del self.cache[key]

    def add_association(self, assoc: Association):
        self.leader.add_association(assoc)
        # Read-your-writes local update
        key = (assoc.id1, assoc.atype)
        if key in self.cache:
            # Avoid duplicates if invalidation fired immediately
            exists = any(a.id2 == assoc.id2 for a in self.cache[key])
            if not exists:
                self.cache[key].append(assoc)
                self.cache[key].sort(key=lambda x: x.timestamp, reverse=True)

    def delete_association(self, id1: int, atype: int, id2: int):
        self.leader.delete_association(id1, atype, id2)
        key = (id1, atype)
        if key in self.cache:
            self.cache[key] = [a for a in self.cache[key] if a.id2 != id2]

    def get_associations(self, id1: int, atype: int) -> List[Association]:
        key = (id1, atype)
        if key not in self.cache:
            self.cache[key] = self.leader.get_associations(id1, atype)
        return self.cache[key]

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]

class GraphEngine:
    def __init__(self, db: Database, leader: LeaderCache, follower: FollowerCache):
        self.db = db
        self.leader = leader
        self.follower = follower

    def get_mutual_friends(self, id1: int, id2: int, atype: int) -> List[int]:
        # 2-hop BFS mutual friend discovery
        # Level 1: Friends of id1
        f1_assocs = self.follower.get_associations(id1, atype)
        f1_set = set(a.id2 for a in f1_assocs)
        
        # Level 2: Friends of id2
        f2_assocs = self.follower.get_associations(id2, atype)
        f2_set = set(a.id2 for a in f2_assocs)
        
        return list(f1_set.intersection(f2_set))

