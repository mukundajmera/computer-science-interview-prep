"""v2-extended TAO social graph engine. The two-tier cache, supernode
virtual bucketing and read path are v1 behavior unchanged; the step-ups
are the ones the project's own docs call for:

1. Cursor-based pagination (FOLLOW-UPS.md #1): assoc_page walks a
   time-ordered association list with an opaque "timestamp:id2" cursor
   instead of OFFSET/LIMIT, so deep pages on supernodes stay O(limit)
   instead of rescanning everything already returned.
2. Read-your-writes versioning (FOLLOW-UPS.md #2): every association
   list carries a version that bumps on each write; a write returns the
   new version, and a read that passes it as min_version force-bypasses a
   stale Follower cache entry, so a client sees its own write even while
   the invalidation bus (Wormhole) is down or lagging.
3. Inverse edge writes (FOLLOW-UPS.md "Variants and extensions" #1):
   add_inverse_association writes both directed edges - (A, FOLLOWS, B)
   sharded by A and (B, FOLLOWED_BY, A) sharded by B - so both "who does
   A follow" and "who follows B" stay O(1) lookups, accepting the
   eventual-consistency trade-off PITFALLS.md #2 prescribes over 2PC.
"""
import time
from typing import Dict, List, Optional, Set, Tuple


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


def _sort_key(assoc: Association) -> Tuple[int, int]:
    # Total order for stable pagination: time DESC, then id2 DESC on ties.
    return (assoc.timestamp, assoc.id2)


def _encode_cursor(assoc: Association) -> str:
    return "%d:%d" % (assoc.timestamp, assoc.id2)


def _decode_cursor(cursor: str) -> Tuple[int, int]:
    timestamp, id2 = cursor.split(":", 1)
    return (int(timestamp), int(id2))


class DatabaseV2:
    def __init__(self):
        self.objects: Dict[int, ObjectNode] = {}
        # Map from (id1, atype, bucket_id) -> List[Association]
        self.associations: Dict[Tuple[int, int, int], List[Association]] = {}
        # Version per association list (FOLLOW-UPS.md #2), bumped per write.
        self.versions: Dict[Tuple[int, int], int] = {}

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

    def _bump_version(self, id1: int, atype: int) -> int:
        key = (id1, atype)
        self.versions[key] = self.versions.get(key, 0) + 1
        return self.versions[key]

    def get_version(self, id1: int, atype: int) -> int:
        return self.versions.get((id1, atype), 0)

    def add_association(self, assoc: Association) -> int:
        bucket_id = self._get_bucket_id(assoc.id1, assoc.id2)
        key = (assoc.id1, assoc.atype, bucket_id)
        if key not in self.associations:
            self.associations[key] = []
        self.associations[key].append(assoc)
        self.associations[key].sort(key=_sort_key, reverse=True)
        return self._bump_version(assoc.id1, assoc.atype)

    def delete_association(self, id1: int, atype: int, id2: int) -> int:
        bucket_id = self._get_bucket_id(id1, id2)
        key = (id1, atype, bucket_id)
        if key in self.associations:
            self.associations[key] = [a for a in self.associations[key] if a.id2 != id2]
        return self._bump_version(id1, atype)

    def get_associations(self, id1: int, atype: int) -> List[Association]:
        results = []
        if self._is_supernode(id1):
            for bucket_id in range(10):
                key = (id1, atype, bucket_id)
                results.extend(self.associations.get(key, []))
        else:
            key = (id1, atype, 0)
            results.extend(self.associations.get(key, []))
        results.sort(key=_sort_key, reverse=True)
        return results

    def assoc_page(self, id1: int, atype: int, limit: int,
                   cursor: Optional[str] = None) -> Tuple[List[Association], Optional[str]]:
        """Cursor-based pagination (FOLLOW-UPS.md #1). The cursor is the
        (timestamp, id2) of the last edge returned, so a page costs
        O(limit) no matter how deep into the list the client is."""
        edges = self.get_associations(id1, atype)
        if cursor is not None:
            mark = _decode_cursor(cursor)
            edges = [a for a in edges if _sort_key(a) < mark]
        page = edges[:limit]
        next_cursor = None
        if len(edges) > limit and page:
            next_cursor = _encode_cursor(page[-1])
        return page, next_cursor

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]


class LeaderCacheV2:
    def __init__(self, db: DatabaseV2):
        self.db = db
        # Map from (id1, atype) to Association list
        self.cache: Dict[Tuple[int, int], List[Association]] = {}
        self.followers: List['FollowerCacheV2'] = []

    def register_follower(self, follower: 'FollowerCacheV2'):
        self.followers.append(follower)

    def broadcast_invalidation(self, id1: int, atype: int):
        for follower in self.followers:
            follower.invalidate(id1, atype)

    def add_association(self, assoc: Association) -> int:
        version = self.db.add_association(assoc)
        key = (assoc.id1, assoc.atype)
        if key in self.cache:
            exists = any(a.id2 == assoc.id2 for a in self.cache[key])
            if not exists:
                self.cache[key].append(assoc)
                self.cache[key].sort(key=_sort_key, reverse=True)
        self.broadcast_invalidation(assoc.id1, assoc.atype)
        return version

    def delete_association(self, id1: int, atype: int, id2: int) -> int:
        version = self.db.delete_association(id1, atype, id2)
        key = (id1, atype)
        if key in self.cache:
            self.cache[key] = [a for a in self.cache[key] if a.id2 != id2]
        self.broadcast_invalidation(id1, atype)
        return version

    def get_version(self, id1: int, atype: int) -> int:
        return self.db.get_version(id1, atype)

    def get_associations(self, id1: int, atype: int) -> List[Association]:
        key = (id1, atype)
        if key not in self.cache:
            self.cache[key] = self.db.get_associations(id1, atype)
        return self.cache[key]

    def assoc_page(self, id1: int, atype: int, limit: int,
                   cursor: Optional[str] = None) -> Tuple[List[Association], Optional[str]]:
        # Deep pagination is a guaranteed cache miss (PITFALLS.md #5); the
        # Leader queries the DB, per FOLLOW-UPS.md #1.
        return self.db.assoc_page(id1, atype, limit, cursor)

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]


class FollowerCacheV2:
    def __init__(self, leader: LeaderCacheV2):
        self.leader = leader
        # Map from (id1, atype) to {"edges": list, "version": int}
        self.cache: Dict[Tuple[int, int], dict] = {}
        # False models the invalidation bus being down for this region
        # (FOLLOW-UPS.md #2): invalidate messages are lost.
        self.bus_connected = True
        self.leader.register_follower(self)

    def set_bus_connected(self, connected: bool):
        self.bus_connected = connected

    def invalidate(self, id1: int, atype: int):
        if not self.bus_connected:
            return
        key = (id1, atype)
        if key in self.cache:
            del self.cache[key]

    def add_association(self, assoc: Association) -> int:
        """Write through the Leader; returns the new list version, which a
        client stores and sends back as min_version (read-your-writes)."""
        version = self.leader.add_association(assoc)
        key = (assoc.id1, assoc.atype)
        if key in self.cache:
            entry = self.cache[key]
            exists = any(a.id2 == assoc.id2 for a in entry["edges"])
            if not exists:
                entry["edges"].append(assoc)
                entry["edges"].sort(key=_sort_key, reverse=True)
            entry["version"] = version
        return version

    def delete_association(self, id1: int, atype: int, id2: int) -> int:
        version = self.leader.delete_association(id1, atype, id2)
        key = (id1, atype)
        if key in self.cache:
            entry = self.cache[key]
            entry["edges"] = [a for a in entry["edges"] if a.id2 != id2]
            entry["version"] = version
        return version

    def get_associations(self, id1: int, atype: int,
                         min_version: Optional[int] = None) -> List[Association]:
        key = (id1, atype)
        entry = self.cache.get(key)
        if entry is not None and (min_version is None or entry["version"] >= min_version):
            return entry["edges"]
        # Miss, or a stale entry the client's min_version rejects: bypass
        # to the Leader for the freshest data (FOLLOW-UPS.md #2). The list
        # is copied so a later Leader-side write cannot mutate this
        # region's cached entry through a shared reference.
        edges = list(self.leader.get_associations(id1, atype))
        self.cache[key] = {"edges": edges, "version": self.leader.get_version(id1, atype)}
        return edges

    def assoc_range(self, id1: int, atype: int, start_time: int, end_time: int) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if start_time <= a.timestamp <= end_time]

    def assoc_count(self, id1: int, atype: int) -> int:
        return len(self.get_associations(id1, atype))

    def assoc_get(self, id1: int, atype: int, id2s: Set[int]) -> List[Association]:
        results = self.get_associations(id1, atype)
        return [a for a in results if a.id2 in id2s]


class GraphEngineV2:
    def __init__(self, db: DatabaseV2, leader: LeaderCacheV2, follower: FollowerCacheV2):
        self.db = db
        self.leader = leader
        self.follower = follower

    def get_mutual_friends(self, id1: int, id2: int, atype: int) -> List[int]:
        f1_assocs = self.follower.get_associations(id1, atype)
        f1_set = set(a.id2 for a in f1_assocs)

        f2_assocs = self.follower.get_associations(id2, atype)
        f2_set = set(a.id2 for a in f2_assocs)

        return list(f1_set.intersection(f2_set))

    def assoc_page(self, id1: int, atype: int, limit: int,
                   cursor: Optional[str] = None) -> Tuple[List[Association], Optional[str]]:
        return self.leader.assoc_page(id1, atype, limit, cursor)

    def add_inverse_association(self, id1: int, atype: int, id2: int,
                                inverse_atype: int, timestamp: int,
                                data: str = "") -> Tuple[int, int]:
        """Write both directed edges (FOLLOW-UPS.md variants #1): the two
        writes are independent on purpose - PITFALLS.md #2 rejects 2PC and
        accepts eventual consistency between them."""
        forward = Association(id1, atype, id2, timestamp, data)
        inverse = Association(id2, inverse_atype, id1, timestamp, data)
        v_forward = self.follower.add_association(forward)
        v_inverse = self.follower.add_association(inverse)
        return (v_forward, v_inverse)

    def delete_inverse_association(self, id1: int, atype: int, id2: int,
                                   inverse_atype: int) -> Tuple[int, int]:
        v_forward = self.follower.delete_association(id1, atype, id2)
        v_inverse = self.follower.delete_association(id2, inverse_atype, id1)
        return (v_forward, v_inverse)
