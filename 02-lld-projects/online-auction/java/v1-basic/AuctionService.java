import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.locks.ReentrantLock;

public class AuctionService {
    private final ConcurrentMap<String, Auction> auctions = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, List<Bid>> auctionBids = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, Bid> highestBids = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, ReentrantLock> auctionLocks = new ConcurrentHashMap<>();

    public Auction createAuction(String itemId, String sellerId, double startingPrice, double reservePrice, Duration duration) {
        String auctionId = UUID.randomUUID().toString();
        Instant startTime = Instant.now();
        Instant endTime = startTime.plus(duration);
        
        Auction auction = new Auction(auctionId, itemId, sellerId, startingPrice, reservePrice, startTime, endTime, AuctionStatus.ACTIVE);
        auctions.put(auctionId, auction);
        auctionBids.put(auctionId, new ArrayList<>());
        auctionLocks.put(auctionId, new ReentrantLock());
        
        return auction;
    }

    public BidResult placeBid(String auctionId, String bidderId, double amount) {
        Auction auction = auctions.get(auctionId);
        if (auction == null) {
            return new BidResult(false, "Auction not found", null);
        }

        ReentrantLock lock = auctionLocks.get(auctionId);
        lock.lock();
        try {
            if (auction.getStatus() != AuctionStatus.ACTIVE) {
                return new BidResult(false, "Auction is closed", highestBids.get(auctionId));
            }

            if (Instant.now().isAfter(auction.getEndTime())) {
                closeAuction(auctionId); // auto-close if time has passed
                return new BidResult(false, "Auction has ended", highestBids.get(auctionId));
            }

            if (auction.getSellerId().equals(bidderId)) {
                return new BidResult(false, "Seller cannot bid on their own auction", highestBids.get(auctionId));
            }

            Bid highestBid = highestBids.get(auctionId);
            double currentHighest = highestBid != null ? highestBid.getAmount() : auction.getStartingPrice();
            
            // First bid must be at least startingPrice. Subsequent bids must be strictly greater than highest.
            if ((highestBid == null && amount < currentHighest) || (highestBid != null && amount <= currentHighest)) {
                return new BidResult(false, "Bid amount must be higher than current highest bid or starting price", highestBids.get(auctionId));
            }

            String bidId = UUID.randomUUID().toString();
            Bid newBid = new Bid(bidId, auctionId, bidderId, amount, System.currentTimeMillis());
            
            highestBids.put(auctionId, newBid);
            auctionBids.get(auctionId).add(newBid);

            return new BidResult(true, "Bid placed successfully", newBid);
        } finally {
            lock.unlock();
        }
    }

    public Auction closeAuction(String auctionId) {
        Auction auction = auctions.get(auctionId);
        if (auction == null) {
            return null;
        }

        ReentrantLock lock = auctionLocks.get(auctionId);
        lock.lock();
        try {
            if (auction.getStatus() != AuctionStatus.ACTIVE) {
                return auction;
            }

            Bid highestBid = highestBids.get(auctionId);
            if (highestBid != null && highestBid.getAmount() >= auction.getReservePrice()) {
                auction.setStatus(AuctionStatus.WON);
            } else {
                auction.setStatus(AuctionStatus.UNSOLD);
            }
            
            return auction;
        } finally {
            lock.unlock();
        }
    }

    public Optional<Bid> getHighestBid(String auctionId) {
        return Optional.ofNullable(highestBids.get(auctionId));
    }

    public List<Bid> getBidHistory(String auctionId) {
        List<Bid> bids = auctionBids.get(auctionId);
        if (bids == null) {
            return new ArrayList<>();
        }
        ReentrantLock lock = auctionLocks.get(auctionId);
        lock.lock();
        try {
            return new ArrayList<>(bids);
        } finally {
            lock.unlock();
        }
    }
}
