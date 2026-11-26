import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from collections import defaultdict
from datetime import datetime


@dataclass
class AdClickEvent:
    event_id: str
    campaign_id: str
    timestamp: datetime
    clicks: int = 1
    # dimensions for aggregation, e.g. {"country": "US"}
    dimensions: Dict[str, str] = field(default_factory=dict)


@dataclass
class AggregationKey:
    campaign_id: str
    window_start: datetime
    dims_hash: str

    def to_string(self) -> str:
        return f"{self.campaign_id}_{self.window_start.isoformat()}_{self.dims_hash}"


class DistributedAdClickAggregator:
    def __init__(self, num_shards: int = 4, num_salts: int = 10, window_size_minutes: int = 1):
        """
        Initializes a distributed ad click aggregator using in-memory structures to simulate shards.
        """
        self.num_shards = num_shards
        self.num_salts = num_salts
        self.window_size_minutes = window_size_minutes

        # In-memory storage for shards: shard_id -> store
        # Store contains partial buckets: salted_key_string -> click_count
        self.shards: Dict[int, Dict[str, int]] = {i: defaultdict(int) for i in range(num_shards)}

        # Idempotence store: shard_id -> set of processed (event_id, window, dims_hash)
        self.processed_events: Dict[int, Set[str]] = {i: set() for i in range(num_shards)}

    def _get_window_start(self, timestamp: datetime) -> datetime:
        """Truncates timestamp to the start of the aggregation window."""
        minute = timestamp.minute - (timestamp.minute % self.window_size_minutes)
        return timestamp.replace(minute=minute, second=0, microsecond=0)

    def _hash_dimensions(self, dimensions: Dict[str, str]) -> str:
        """Returns a deterministic hash for a dictionary of dimensions."""
        if not dimensions:
            return "none"
        sorted_dims = sorted(dimensions.items())
        dims_str = json.dumps(sorted_dims)
        return hashlib.sha256(dims_str.encode('utf-8')).hexdigest()[:8]

    def _get_shard_id(self, key_string: str) -> int:
        """Deterministically routes a key to a shard."""
        return int(hashlib.md5(key_string.encode('utf-8')).hexdigest(), 16) % self.num_shards

    def _get_salt(self, event_id: str) -> int:
        """Deterministically assigns a salt based on event_id."""
        return int(hashlib.md5(event_id.encode('utf-8')).hexdigest(), 16) % self.num_salts

    def process_event(self, event: AdClickEvent) -> bool:
        """
        Process an event and return True if it was added, False if it was a duplicate (replay-safe).
        Demonstrates deterministic partition routing and replay-safe aggregate mutations.
        """
        window_start = self._get_window_start(event.timestamp)
        dims_hash = self._hash_dimensions(event.dimensions)

        agg_key = AggregationKey(event.campaign_id, window_start, dims_hash)
        agg_key_str = agg_key.to_string()

        # Generate idempotency key
        idem_key = f"{event.event_id}_{agg_key_str}"

        # Salt the key to distribute hot campaigns
        salt = self._get_salt(event.event_id)
        salted_key_str = f"{agg_key_str}_salt_{salt}"

        # Determine shard based on salted key to spread hot keys across shards
        shard_id = self._get_shard_id(salted_key_str)

        # Check idempotence to ensure replay-safety
        if idem_key in self.processed_events[shard_id]:
            return False

        # Apply mutation
        self.shards[shard_id][salted_key_str] += event.clicks
        self.processed_events[shard_id].add(idem_key)

        return True

    def query_aggregate(self, campaign_id: str, window_start: datetime, dimensions: Optional[Dict[str, str]] = None) -> int:
        """
        Query aggregate by merging salted buckets across all relevant shards.
        """
        if dimensions is None:
            dimensions = {}

        dims_hash = self._hash_dimensions(dimensions)
        agg_key = AggregationKey(campaign_id, window_start, dims_hash)
        agg_key_str = agg_key.to_string()

        total_clicks = 0

        # For a query, we must look up all possible salts and merge them
        for salt in range(self.num_salts):
            salted_key_str = f"{agg_key_str}_salt_{salt}"
            shard_id = self._get_shard_id(salted_key_str)

            clicks = self.shards[shard_id].get(salted_key_str, 0)
            total_clicks += clicks

        return total_clicks

    def get_audit_trail(self, shard_id: int) -> List[str]:
        """
        Return the list of processed idempotence keys for a shard for audit visibility.
        """
        if shard_id not in self.processed_events:
            return []
        return sorted(list(self.processed_events[shard_id]))
