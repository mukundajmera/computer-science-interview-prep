import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V1_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic"))
if V1_DIR not in sys.path:
    sys.path.insert(0, V1_DIR)

from auction_service import AuctionService, AuctionState


class AuctionServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = AuctionService()

    def test_auction_state_machine(self):
        aid = self.service.create_auction("item1", "seller1", 100, 10, 5)
        auction = self.service.get_auction(aid)
        self.assertEqual(auction.state, AuctionState.PENDING)
        
        self.service.start_auction(aid)
        self.assertEqual(auction.state, AuctionState.ACTIVE)
        
        # Fast forward time to complete
        auction.end_time = time.time() - 1
        self.service.evaluate_auction(aid)
        self.assertEqual(auction.state, AuctionState.COMPLETED)

    def test_atomic_bid_increment(self):
        aid = self.service.create_auction("item2", "seller2", 100, 10, 10)
        self.service.start_auction(aid)
        
        # Valid bid
        res = self.service.place_bid(aid, "bidder1", 50)
        self.assertTrue(res)
        
        # Invalid bid: not meeting minimum increment
        res = self.service.place_bid(aid, "bidder2", 55)
        self.assertFalse(res)
        
        # Valid bid
        res = self.service.place_bid(aid, "bidder3", 60)
        self.assertTrue(res)

    def test_reserve_price_evaluation(self):
        aid = self.service.create_auction("item3", "seller3", 100, 10, 5)
        self.service.start_auction(aid)
        
        self.service.place_bid(aid, "bidder1", 90)
        
        auction = self.service.get_auction(aid)
        auction.end_time = time.time() - 1
        
        winner = self.service.evaluate_auction(aid)
        self.assertIsNone(winner)  # Highest bid was 90, reserve is 100
        
        # Reset and try again with meeting reserve price
        aid2 = self.service.create_auction("item4", "seller4", 100, 10, 5)
        self.service.start_auction(aid2)
        self.service.place_bid(aid2, "bidder1", 105)
        
        auction2 = self.service.get_auction(aid2)
        auction2.end_time = time.time() - 1
        
        winner2 = self.service.evaluate_auction(aid2)
        self.assertIsNotNone(winner2)
        self.assertEqual(winner2.bidder_id, "bidder1")

    def test_auction_countdown_timer(self):
        aid = self.service.create_auction("item5", "seller5", 50, 0.1, 5)
        self.service.start_auction(aid)
        
        self.assertTrue(self.service.place_bid(aid, "bidder1", 60))
        
        # Wait for duration to pass
        time.sleep(0.15)
        
        # Should be rejected because time passed
        self.assertFalse(self.service.place_bid(aid, "bidder2", 70))
        
        winner = self.service.evaluate_auction(aid)
        self.assertIsNotNone(winner)
        self.assertEqual(winner.amount, 60)


if __name__ == "__main__":
    unittest.main()
