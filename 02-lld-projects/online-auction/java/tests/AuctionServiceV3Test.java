import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Optional;

class MockRepository implements AuctionRepository {
    @Override
    public void save(String key, String value) {}
    @Override
    public Optional<String> find(String key) { return Optional.empty(); }
}

public class AuctionServiceV3Test {
    private AuctionServiceV3 service;

    @BeforeEach
    public void setUp() {
        service = new AuctionServiceV3(new MockRepository());
    }

    @Test
    public void testEnglishProxyTieOrder() {
        String aid = service.createAuction("a1", "seller1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        boolean bidSuccess1 = service.placeBid(aid, "b1", 200, "idmp1", 100.0);
        assertTrue(bidSuccess1);
        assertTrue(service.placeBid(aid, "b2", 200, "idmp2", 150.0));
        
        assertTrue(service.settleAuction(aid, 1001.0));
        Auction auction = service.auctions.get(aid);
        assertEquals(AuctionState.SETTLED, auction.state);
        assertEquals("b1", auction.winnerId);
        assertEquals(200L, auction.winningPrice);
    }

    @Test
    public void testVickreySealedBid() {
        String aid = service.createAuction("a2", "seller2", 100, 10, 1000.0, BidPolicy.VICKREY);
        service.openAuction(aid);
        
        assertTrue(service.placeBid(aid, "b1", 200, "idmp1", 100.0));
        assertTrue(service.placeBid(aid, "b2", 300, "idmp2", 150.0));
        assertTrue(service.placeBid(aid, "b3", 150, "idmp3", 200.0));
        
        assertTrue(service.settleAuction(aid, 1001.0));
        Auction auction = service.auctions.get(aid);
        assertEquals(AuctionState.SETTLED, auction.state);
        assertEquals("b2", auction.winnerId);
        assertEquals(200L, auction.winningPrice);
    }

    @Test
    public void testLateBidAndSettlementReplay() {
        String aid = service.createAuction("a3", "seller3", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertTrue(service.placeBid(aid, "b1", 150, "id1", 100.0));
        assertFalse(service.placeBid(aid, "b2", 200, "id2", 1001.0));
        
        assertTrue(service.settleAuction(aid, 1001.0));
        Auction auction = service.auctions.get(aid);
        assertEquals("b1", auction.winnerId);
        
        assertTrue(service.settleAuction(aid, 1005.0));
        assertEquals("b1", auction.winnerId);
        assertEquals(AuctionState.SETTLED, auction.state);
    }

    @Test
    public void testAntiSnipeExtensions() {
        String aid = service.createAuction("a4", "s1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertTrue(service.placeBid(aid, "b1", 150, "id1", 500.0));
        Auction auction = service.auctions.get(aid);
        assertEquals(1000.0, auction.endTime);
        
        assertTrue(service.placeBid(aid, "b2", 200, "id2", 900.0));
        assertEquals(1300.0, auction.endTime);
        assertEquals(1, auction.extensionCount);
        
        for (int i = 0; i < 4; i++) {
            assertTrue(service.placeBid(aid, "b" + (i + 3), 200 + (i + 1) * 10, "id3_" + i, 1290.0 + i * 300.0));
        }
        
        assertEquals(5, auction.extensionCount);
        double currentEnd = auction.endTime;
        assertTrue(service.placeBid(aid, "bx", 1000, "idx", currentEnd - 10));
        assertEquals(currentEnd, auction.endTime);
    }

    @Test
    public void testMoneyRepresentation() {
        String aid = service.createAuction("a5", "s1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertFalse(service.placeBid(aid, "b1", -50, "id1", 100.0));
        assertFalse(service.placeBid(aid, "b1", 0, "id2", 100.0));
        assertTrue(service.placeBid(aid, "b1", 150, "id4", 100.0));
    }
    
    @Test
    public void testIdempotency() {
        String aid = service.createAuction("a6", "s1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertTrue(service.placeBid(aid, "b1", 150, "idmp1", 100.0));
        assertTrue(service.placeBid(aid, "b1", 150, "idmp1", 100.0));
        
        Auction auction = service.auctions.get(aid);
        assertEquals(1, auction.bids.size());
    }
    
    @Test
    public void testEnglishProxyExactPricing() {
        String aid = service.createAuction("a7", "s1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertTrue(service.placeBid(aid, "b1", 200, "id1", 100.0));
        assertTrue(service.placeBid(aid, "b2", 150, "id2", 150.0));
        
        assertTrue(service.settleAuction(aid, 1001.0));
        Auction auction = service.auctions.get(aid);
        assertEquals("b1", auction.winnerId);
        assertEquals(160L, auction.winningPrice);
    }

    @Test
    public void testRollbackFixture() {
        String aid = service.createAuction("a_rollback", "seller1", 100, 10, 1000.0, BidPolicy.ENGLISH_PROXY);
        service.openAuction(aid);
        
        assertFalse(service.placeBid(aid, "b1", 50, "idmp1", 100.0));
        assertEquals(0, service.auctions.get(aid).bids.size());
    }
}
