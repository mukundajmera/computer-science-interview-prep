import unittest
from datetime import datetime, timedelta, timezone
import sys
import os

# Allow import for versioned directory with hyphens
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
from ad_click_aggregator import InMemoryAdClickAggregator, ClickEvent


class TestAdClickAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = InMemoryAdClickAggregator()
        self.now = datetime.now(timezone.utc)

    def test_valid_ingest_and_query(self):
        event = ClickEvent(
            event_id="e1",
            event_time=self.now,
            campaign_id="c1",
            ad_group_id="ag1",
            publisher_id="p1"
        )
        self.aggregator.record_click(event)

        start_time = self.now - timedelta(minutes=1)
        end_time = self.now + timedelta(minutes=1)

        clicks = self.aggregator.get_campaign_clicks("c1", start_time, end_time)
        self.assertEqual(clicks, 1)

        ag_clicks = self.aggregator.get_ad_group_clicks("ag1", start_time, end_time)
        self.assertEqual(ag_clicks, 1)

        pub_clicks = self.aggregator.get_publisher_clicks("p1", start_time, end_time)
        self.assertEqual(pub_clicks, 1)


    def test_duplicate_delivery(self):
        event = ClickEvent(
            event_id="e1",
            event_time=self.now,
            campaign_id="c1",
            ad_group_id="ag1",
            publisher_id="p1"
        )

        # Ingest twice
        self.aggregator.record_click(event)
        self.aggregator.record_click(event)

        start_time = self.now - timedelta(minutes=1)
        end_time = self.now + timedelta(minutes=1)
        clicks = self.aggregator.get_campaign_clicks("c1", start_time, end_time)

        # Deduplication should yield 1 click
        self.assertEqual(clicks, 1)

    def test_window_boundaries_dimension_separation(self):
        base_time = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Event exactly on the boundary
        e1 = ClickEvent("e1", base_time, "c1", "ag1", "p1")
        # Event at 12:00:30
        e2 = ClickEvent("e2", base_time + timedelta(seconds=30), "c1", "ag1", "p1")
        # Event at 12:01:00 (next window)
        e3 = ClickEvent("e3", base_time + timedelta(minutes=1), "c1", "ag1", "p1")
        # Event in another campaign
        e4 = ClickEvent("e4", base_time, "c2", "ag1", "p1")

        # Event in another publisher
        e5 = ClickEvent("e5", base_time, "c1", "ag1", "p2")

        for e in [e1, e2, e3, e4, e5]:
            self.aggregator.record_click(e)

        # Query 12:00 to 12:01, should include e1, e2, and e5
        clicks_c1 = self.aggregator.get_campaign_clicks("c1", base_time, base_time + timedelta(minutes=1))
        self.assertEqual(clicks_c1, 3)

        # Query 12:01 to 12:02
        clicks_c1_next = self.aggregator.get_campaign_clicks("c1", base_time + timedelta(minutes=1), base_time + timedelta(minutes=2))
        self.assertEqual(clicks_c1_next, 1)

        # Dimension separation (Campaign)
        clicks_c2 = self.aggregator.get_campaign_clicks("c2", base_time, base_time + timedelta(minutes=1))
        self.assertEqual(clicks_c2, 1)

        # Dimension separation (Publisher)
        clicks_p1 = self.aggregator.get_publisher_clicks("p1", base_time, base_time + timedelta(minutes=1))
        self.assertEqual(clicks_p1, 3) # e1, e2, e4

        clicks_p2 = self.aggregator.get_publisher_clicks("p2", base_time, base_time + timedelta(minutes=1))
        self.assertEqual(clicks_p2, 1) # e5

    def test_invalid_input(self):
        # Missing event_id
        with self.assertRaises(ValueError):
            self.aggregator.record_click(ClickEvent("", self.now, "c1", "ag1", "p1"))

        # Missing campaign_id
        with self.assertRaises(ValueError):
            self.aggregator.record_click(ClickEvent("e1", self.now, "", "ag1", "p1"))

        # Missing ad_group_id
        with self.assertRaises(ValueError):
            self.aggregator.record_click(ClickEvent("e1", self.now, "c1", "", "p1"))

        # Missing publisher_id
        with self.assertRaises(ValueError):
            self.aggregator.record_click(ClickEvent("e1", self.now, "c1", "ag1", ""))

        # Missing event_time (using None to trigger error)
        with self.assertRaises(ValueError):
            self.aggregator.record_click(ClickEvent("e1", None, "c1", "ag1", "p1"))

if __name__ == '__main__':
    unittest.main()
