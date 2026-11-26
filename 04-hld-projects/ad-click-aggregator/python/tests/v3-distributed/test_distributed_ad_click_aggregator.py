import unittest
from datetime import datetime, timezone, timedelta
import sys
import os

# dynamic sys.path import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))
from distributed_ad_click_aggregator import DistributedAdClickAggregator, AdClickEvent


class TestDistributedAdClickAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = DistributedAdClickAggregator(num_shards=4, num_salts=10, window_size_minutes=1)
        self.now = datetime.now(timezone.utc)
        self.window_start = self.aggregator._get_window_start(self.now)

    def test_stable_routing(self):
        """Test that events with same ID route to the same shard/salt and dimensions hash properly."""
        event1 = AdClickEvent(
            event_id="evt1",
            campaign_id="campA",
            timestamp=self.now,
            clicks=1,
            dimensions={"country": "US", "browser": "Chrome"}
        )

        event2 = AdClickEvent(
            event_id="evt2",
            campaign_id="campA",
            timestamp=self.now,
            clicks=1,
            dimensions={"browser": "Chrome", "country": "US"} # reversed order, same data
        )

        hash1 = self.aggregator._hash_dimensions(event1.dimensions)
        hash2 = self.aggregator._hash_dimensions(event2.dimensions)
        self.assertEqual(hash1, hash2, "Dimension hashing must be order-independent")

        # Verify salt routing
        salt1 = self.aggregator._get_salt("evt1")
        salt1_again = self.aggregator._get_salt("evt1")
        self.assertEqual(salt1, salt1_again, "Salt must be deterministic for the same event ID")

    def test_retry_idempotence(self):
        """Test replay-safety with idempotence key (event_id, window, dims_hash)."""
        event = AdClickEvent(
            event_id="unique_evt_1",
            campaign_id="campA",
            timestamp=self.now,
            clicks=2,
            dimensions={"country": "US"}
        )

        # First process should succeed
        is_new = self.aggregator.process_event(event)
        self.assertTrue(is_new, "First processing of event should be new")

        # Immediate replay should be ignored
        is_new_replay = self.aggregator.process_event(event)
        self.assertFalse(is_new_replay, "Replayed event should be ignored")

        # Query should show only 2 clicks, not 4
        clicks = self.aggregator.query_aggregate("campA", self.window_start, {"country": "US"})
        self.assertEqual(clicks, 2)

    def test_salted_merge(self):
        """Test that salted buckets are correctly merged on query."""
        # Process many events for same campaign to hit different salts
        for i in range(100):
            event = AdClickEvent(
                event_id=f"evt_{i}",
                campaign_id="hot_campaign",
                timestamp=self.now,
                clicks=1,
                dimensions={}
            )
            self.aggregator.process_event(event)

        # All 100 clicks should be aggregated back together
        total_clicks = self.aggregator.query_aggregate("hot_campaign", self.window_start, {})
        self.assertEqual(total_clicks, 100)

        # Verify that they are distributed across multiple shards/salts
        non_empty_shards = 0
        for shard_id, store in self.aggregator.shards.items():
            if len(store) > 0:
                non_empty_shards += 1

        # Since we use 10 salts and 4 shards, for 100 events,
        # it's highly likely they are distributed across multiple shards
        self.assertGreater(non_empty_shards, 1, "Hot keys should be distributed across multiple shards")

    def test_audit_visibility(self):
        """Test that the idempotence store maintains an auditable trail."""
        event1 = AdClickEvent(event_id="aud_1", campaign_id="campA", timestamp=self.now, clicks=1)
        event2 = AdClickEvent(event_id="aud_2", campaign_id="campA", timestamp=self.now, clicks=1)

        self.aggregator.process_event(event1)
        self.aggregator.process_event(event2)

        # Find which shard got aud_1
        aud1_found = False
        aud2_found = False
        for shard_id in range(self.aggregator.num_shards):
            trail = self.aggregator.get_audit_trail(shard_id)
            if any("aud_1" in entry for entry in trail):
                aud1_found = True
            if any("aud_2" in entry for entry in trail):
                aud2_found = True

        self.assertTrue(aud1_found)
        self.assertTrue(aud2_found)


if __name__ == '__main__':
    unittest.main()
