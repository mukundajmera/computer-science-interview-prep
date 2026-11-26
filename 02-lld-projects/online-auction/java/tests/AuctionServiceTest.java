import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class AuctionServiceTest {

    private AuctionService service;

    @BeforeEach
    void setUp() {
        service = new AuctionService();
    }

    @Test
    void testAuctionLifecycleAndAscendingBidding() {
        Auction auction = service.createAuction("item1", "seller1", 10.0, 50.0, Duration.ofMinutes(10));
        Assertions.assertNotNull(auction.getAuctionId());
        Assertions.assertEquals(AuctionStatus.ACTIVE, auction.getStatus());

        // First bid
        BidResult res1 = service.placeBid(auction.getAuctionId(), "bidder1", 15.0);
        Assertions.assertTrue(res1.isSuccess());
        Assertions.assertEquals(15.0, res1.getHighestBid().getAmount());

        // Second bid higher
        BidResult res2 = service.placeBid(auction.getAuctionId(), "bidder2", 20.0);
        Assertions.assertTrue(res2.isSuccess());
        Assertions.assertEquals(20.0, res2.getHighestBid().getAmount());
        
        Optional<Bid> highest = service.getHighestBid(auction.getAuctionId());
        Assertions.assertTrue(highest.isPresent());
        Assertions.assertEquals(20.0, highest.get().getAmount());
        
        List<Bid> history = service.getBidHistory(auction.getAuctionId());
        Assertions.assertEquals(2, history.size());
    }

    @Test
    void testRejectedInvalidBids() {
        Auction auction = service.createAuction("item2", "seller2", 20.0, 100.0, Duration.ofMinutes(10));
        
        // Lower than starting price
        BidResult res1 = service.placeBid(auction.getAuctionId(), "bidder1", 10.0);
        Assertions.assertFalse(res1.isSuccess());

        // Valid bid
        BidResult res2 = service.placeBid(auction.getAuctionId(), "bidder1", 25.0);
        Assertions.assertTrue(res2.isSuccess());

        // Lower or equal to current highest bid
        BidResult res3 = service.placeBid(auction.getAuctionId(), "bidder2", 25.0);
        Assertions.assertFalse(res3.isSuccess());

        BidResult res4 = service.placeBid(auction.getAuctionId(), "bidder3", 20.0);
        Assertions.assertFalse(res4.isSuccess());
        
        // Seller bidding on own auction
        BidResult res5 = service.placeBid(auction.getAuctionId(), "seller2", 50.0);
        Assertions.assertFalse(res5.isSuccess());
    }

    @Test
    void testReservePriceMet() {
        Auction auction = service.createAuction("item3", "seller3", 10.0, 100.0, Duration.ofMinutes(10));
        service.placeBid(auction.getAuctionId(), "bidder1", 105.0);
        
        Auction closedAuction = service.closeAuction(auction.getAuctionId());
        Assertions.assertEquals(AuctionStatus.WON, closedAuction.getStatus());
    }
    
    @Test
    void testReservePriceNotMet() {
        Auction auction = service.createAuction("item4", "seller4", 10.0, 100.0, Duration.ofMinutes(10));
        service.placeBid(auction.getAuctionId(), "bidder1", 90.0);
        
        Auction closedAuction = service.closeAuction(auction.getAuctionId());
        Assertions.assertEquals(AuctionStatus.UNSOLD, closedAuction.getStatus());
    }

    @Test
    void testConcurrentBidContention() throws InterruptedException {
        Auction auction = service.createAuction("item5", "seller5", 1.0, 10.0, Duration.ofMinutes(10));
        String auctionId = auction.getAuctionId();

        int threadCount = 100;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threadCount);
        
        AtomicInteger successCount = new AtomicInteger(0);

        for (int i = 0; i < threadCount; i++) {
            final int bidderId = i;
            executor.submit(() -> {
                try {
                    startLatch.await();
                    // Each thread tries to place a bid of a strictly higher fixed value
                    // Or they can all try to bid 10.0, only one should succeed
                    BidResult result = service.placeBid(auctionId, "bidder" + bidderId, 5.0);
                    if (result.isSuccess()) {
                        successCount.incrementAndGet();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        startLatch.countDown();
        doneLatch.await(5, TimeUnit.SECONDS);
        executor.shutdown();

        // Only one bid of exactly 5.0 can succeed since subsequent bids of 5.0 will be rejected
        Assertions.assertEquals(1, successCount.get());
        
        Optional<Bid> highest = service.getHighestBid(auctionId);
        Assertions.assertTrue(highest.isPresent());
        Assertions.assertEquals(5.0, highest.get().getAmount());
    }
}
