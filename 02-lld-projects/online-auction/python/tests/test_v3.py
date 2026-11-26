import os
import sys
import unittest

BASE_DIR = os.path.dirname(__file__)
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized"))
if V3_DIR not in sys.path:
    sys.path.insert(0, V3_DIR)

from auction_service_v3 import AuctionServiceV3
from auction_state import BidPolicy, AuctionState

class MockRepository:
    def __init__(self):
        self.data = {}
    def save(self, key: str, value: str) -> None:
        self.data[key] = value
    def find(self, key: str) -> str:
        return self.data.get(key)

class AuctionServiceV3Test(unittest.TestCase):
    def setUp(self):
        self.repo = MockRepository()
        self.service = AuctionServiceV3(self.repo)

    def test_english_proxy_tie_order(self):
        aid = self.service.create_auction("a1", "seller1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY)
        self.service.open_auction(aid)
        
        # Two bidders bid the same amount, b1 bids first
        bid_success_1 = self.service.place_bid(aid, "b1", 200, "idmp1", 100.0)
        self.assertTrue(bid_success_1)
        self.assertTrue(self.service.place_bid(aid, "b2", 200, "idmp2", 150.0))
        
        self.service.settle_auction(aid, 1001.0)
        auction = self.service.auctions[aid]
        self.assertEqual(auction.state, AuctionState.SETTLED)
        self.assertEqual(auction.winner_id, "b1")
        self.assertEqual(auction.winning_price, 200) # second highest is 200, + min_increment doesn't exceed winner max

    def test_vickrey_sealed_bid(self):
        aid = self.service.create_auction("a2", "seller2", 100, 10, 1000.0, BidPolicy.VICKREY)
        self.service.open_auction(aid)
        
        self.assertTrue(self.service.place_bid(aid, "b1", 200, "idmp1", 100.0))
        self.assertTrue(self.service.place_bid(aid, "b2", 300, "idmp2", 150.0))
        self.assertTrue(self.service.place_bid(aid, "b3", 150, "idmp3", 200.0))
        
        self.service.settle_auction(aid, 1001.0)
        auction = self.service.auctions[aid]
        self.assertEqual(auction.state, AuctionState.SETTLED)
        self.assertEqual(auction.winner_id, "b2")
        self.assertEqual(auction.winning_price, 200) # Pays second highest bid

    def test_late_bid_and_settlement_replay(self):
        aid = self.service.create_auction("a3", "seller3", 100, 10, 1000.0)
        self.service.open_auction(aid)
        
        self.assertTrue(self.service.place_bid(aid, "b1", 150, "id1", 100.0))
        self.assertFalse(self.service.place_bid(aid, "b2", 200, "id2", 1001.0)) # late bid rejected
        
        self.assertTrue(self.service.settle_auction(aid, 1001.0))
        auction = self.service.auctions[aid]
        self.assertEqual(auction.winner_id, "b1")
        
        # replay
        self.assertTrue(self.service.settle_auction(aid, 1005.0))
        self.assertEqual(auction.winner_id, "b1")
        self.assertEqual(auction.state, AuctionState.SETTLED)

    def test_anti_snipe_extensions(self):
        aid = self.service.create_auction("a4", "s1", 100, 10, 1000.0)
        self.service.open_auction(aid)
        
        # normal bid
        self.assertTrue(self.service.place_bid(aid, "b1", 150, "id1", 500.0))
        auction = self.service.auctions[aid]
        self.assertEqual(auction.end_time, 1000.0)
        
        # snipe bid within 300s window
        self.assertTrue(self.service.place_bid(aid, "b2", 200, "id2", 900.0))
        self.assertEqual(auction.end_time, 1300.0)
        self.assertEqual(auction.extension_count, 1)
        
        # hit limit
        for i in range(4):
            self.assertTrue(self.service.place_bid(aid, f"b{i+3}", 200 + (i+1)*10, f"id3_{i}", 1290.0 + i*300))
        
        self.assertEqual(auction.extension_count, 5)
        # Next snipe won't extend
        current_end = auction.end_time
        self.assertTrue(self.service.place_bid(aid, "bx", 1000, "idx", current_end - 10))
        self.assertEqual(auction.end_time, current_end)

    def test_money_representation(self):
        aid = self.service.create_auction("a5", "s1", 100, 10, 1000.0)
        self.service.open_auction(aid)
        
        self.assertFalse(self.service.place_bid(aid, "b1", -50, "id1", 100.0))
        self.assertFalse(self.service.place_bid(aid, "b1", 0, "id2", 100.0))
        self.assertFalse(self.service.place_bid(aid, "b1", 100.5, "id3", 100.0)) # non-integer
        self.assertTrue(self.service.place_bid(aid, "b1", 150, "id4", 100.0))
        
    def test_idempotency(self):
        aid = self.service.create_auction("a6", "s1", 100, 10, 1000.0)
        self.service.open_auction(aid)
        
        self.assertTrue(self.service.place_bid(aid, "b1", 150, "idmp1", 100.0))
        self.assertTrue(self.service.place_bid(aid, "b1", 150, "idmp1", 100.0)) # returns True, but no double bid
        
        auction = self.service.auctions[aid]
        self.assertEqual(len(auction.bids), 1)
        
    def test_english_proxy_exact_pricing(self):
        aid = self.service.create_auction("a7", "s1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY)
        self.service.open_auction(aid)
        
        self.assertTrue(self.service.place_bid(aid, "b1", 200, "id1", 100.0))
        self.assertTrue(self.service.place_bid(aid, "b2", 150, "id2", 150.0))
        
        self.service.settle_auction(aid, 1001.0)
        auction = self.service.auctions[aid]
        self.assertEqual(auction.winner_id, "b1")
        self.assertEqual(auction.winning_price, 160) # 150 + 10

    def test_rollback_fixture(self):
        aid = self.service.create_auction("a_rollback", "seller1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY)
        self.service.open_auction(aid)
        
        self.assertFalse(self.service.place_bid(aid, "b1", 50, "idmp1", 100.0))
        self.assertEqual(len(self.service.auctions[aid].bids), 0)

if __name__ == "__main__":
    unittest.main()
