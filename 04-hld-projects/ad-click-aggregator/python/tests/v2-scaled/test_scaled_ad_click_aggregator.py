import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_ad_click_aggregator import ScaledAdClickAggregator, ClickEvent

class TestScaledAdClickAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = ScaledAdClickAggregator(
            late_event_bound_ms=1000,
            dedup_retention_ms=5000,
            num_partitions=2
        )

    def test_partition_routing(self):
        event1 = ClickEvent(event_id="e1", campaign_id="c1", advertiser_id="a1", event_time_ms=100)
        event2 = ClickEvent(event_id="e2", campaign_id="c1", advertiser_id="a1", event_time_ms=100)

        self.aggregator.ingest_event(event1)
        self.aggregator.ingest_event(event2)

        # Check that events are in the partitioned log
        log = self.aggregator.ingest_log
        p1 = log.get_partition(event1.event_id)
        p2 = log.get_partition(event2.event_id)

        # Verify event1 is in p1 and event2 is in p2
        self.assertIn(event1, log.get_events(p1))
        self.assertIn(event2, log.get_events(p2))

    def test_dedup_retention_and_expiry(self):
        self.aggregator.set_time(1000)
        event = ClickEvent(event_id="e1", campaign_id="c1", advertiser_id="a1", event_time_ms=100)

        # First ingest
        self.assertTrue(self.aggregator.ingest_event(event))
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 1)

        # Replay (idempotent)
        self.aggregator.set_time(2000)
        self.assertTrue(self.aggregator.ingest_event(event))
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 1) # Still 1

        # Expire dedup index
        self.aggregator.set_time(6001) # 6001 - 1000 = 5001 > 5000
        self.aggregator.expire_dedup_index()

        # Ingest again, should count as new because dedup expired (in real world, this is acceptable for very old replays beyond retention)
        self.assertTrue(self.aggregator.ingest_event(event))
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 2)

    def test_late_correction_visibility(self):
        # Set watermark to 2000
        e1 = ClickEvent(event_id="e1", campaign_id="c1", advertiser_id="a1", event_time_ms=2000)
        self.aggregator.set_time(2000)
        self.assertTrue(self.aggregator.ingest_event(e1))
        self.assertEqual(self.aggregator.watermark_ms, 2000)

        # Late event within bound (1000ms bound) -> event time 1500
        e2 = ClickEvent(event_id="e2", campaign_id="c1", advertiser_id="a1", event_time_ms=1500)
        self.aggregator.set_time(2500)
        self.assertTrue(self.aggregator.ingest_event(e2))

        # Check clicks
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 2)

        # Check corrections
        corrections = self.aggregator.get_corrections()
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0].event_id, "e2")
        self.assertEqual(corrections[0].delta, 1)

    def test_out_of_bound_event(self):
        # Set watermark to 5000
        e1 = ClickEvent(event_id="e1", campaign_id="c1", advertiser_id="a1", event_time_ms=5000)
        self.aggregator.set_time(5000)
        self.assertTrue(self.aggregator.ingest_event(e1))
        self.assertEqual(self.aggregator.watermark_ms, 5000)

        # Late event out of bound (1000ms bound) -> event time 3000 (< 5000 - 1000)
        e2 = ClickEvent(event_id="e2", campaign_id="c1", advertiser_id="a1", event_time_ms=3000)
        self.aggregator.set_time(6000)

        self.assertFalse(self.aggregator.ingest_event(e2)) # Should drop
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 1) # Only e1
        self.assertEqual(len(self.aggregator.get_corrections()), 0)

    def test_replay_idempotence(self):
        self.aggregator.set_time(1000)
        e1 = ClickEvent(event_id="e1", campaign_id="c1", advertiser_id="a1", event_time_ms=1000)

        # Ingest
        self.assertTrue(self.aggregator.ingest_event(e1))
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 1)

        # Replay identical event
        self.assertTrue(self.aggregator.ingest_event(e1))
        self.assertEqual(self.aggregator.get_campaign_clicks("c1"), 1)

        # Check log doesn't have duplicates for the same event
        log_events = self.aggregator.ingest_log.get_events(self.aggregator.ingest_log.get_partition("e1"))
        self.assertEqual(len([e for e in log_events if e.event_id == "e1"]), 1)

if __name__ == '__main__':
    unittest.main()
