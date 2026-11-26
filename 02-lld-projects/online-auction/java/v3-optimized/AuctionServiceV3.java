import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.List;
import java.util.ArrayList;

public class AuctionServiceV3 implements BidService  {
    private final AuctionRepository repository;
    final Map<String, Auction> auctions = new HashMap<>();
    private final Map<BidPolicy, BidValidationPolicy> policies = new HashMap<>();
    private final Object lock = new Object();

    public AuctionServiceV3(AuctionRepository repository) {
        this.repository = repository;
        this.policies.put(BidPolicy.ENGLISH_PROXY, new EnglishProxyBidPolicy());
        this.policies.put(BidPolicy.VICKREY, new VickreySealedBidPolicy());
    }

    public void upsert(String key, String value) {
        if (repository != null) {
            repository.save(key, value);
        }
    }

    public Optional<String> get(String key) {
        if (repository != null) {
            return repository.find(key);
        }
        return Optional.empty();
    }
    
    public String createAuction(String auctionId, String sellerId, long startPrice, long minIncrement, double endTime, BidPolicy policy) {
        synchronized (lock) {
            Auction auction = new Auction(auctionId, sellerId, startPrice, minIncrement, endTime, policy, 5, 300.0, 300.0);
            auctions.put(auctionId, auction);
            return auctionId;
        }
    }
    
    public void openAuction(String auctionId) {
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction != null && auction.state == AuctionState.DRAFT) {
                auction.state = AuctionState.OPEN;
            }
        }
    }

    
    public boolean placeBid(String auctionId, String bidderId, long amount, String idempotencyKey, double currentTime) {
        boolean isValidAmount = amount > 0;
        if (!isValidAmount) return false;
        
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction == null || auction.state != AuctionState.OPEN) return false;
            if (currentTime > auction.endTime) return false;
            if (bidderId.equals(auction.sellerId)) return false;
            
            for (Bid bid : auction.bids) {
                if (idempotencyKey != null && !idempotencyKey.isEmpty() && idempotencyKey.equals(bid.idempotencyKey)) {
                    return true;
                }
            }
            
            BidValidationPolicy policyImpl = policies.get(auction.policy);
            if (policyImpl == null) return false;
            
            long highestBid = auction.startPrice - auction.minIncrement;
            if (auction.policy == BidPolicy.ENGLISH_PROXY && !auction.bids.isEmpty()) {
                long max = auction.startPrice - auction.minIncrement;
                for (Bid b : auction.bids) {
                    if (b.amount > max) {
                        max = b.amount;
                    }
                }
                highestBid = max;
            }
            
            if (!policyImpl.isValidBid(highestBid, amount, auction.state, auction)) return false;
            
            auction.bids.add(new Bid(bidderId, amount, currentTime, idempotencyKey));
            
            // anti-snipe
            if (currentTime >= auction.endTime - auction.extensionWindow) {
                if (auction.extensionCount < auction.extensionLimit) {
                    auction.endTime += auction.extensionDuration;
                    auction.extensionCount++;
                }
            }
            
            return true;
        }
    }
    
    public boolean settleAuction(String auctionId, double currentTime) {
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction == null) return false;
            if (auction.state == AuctionState.SETTLED) return true;
            if (currentTime <= auction.endTime) return false;
            
            auction.state = AuctionState.CLOSED;
            
            if (auction.bids.isEmpty()) {
                auction.state = AuctionState.SETTLED;
                return true;
            }
            
            List<Bid> sortedBids = new ArrayList<>(auction.bids);
            sortedBids.sort((b1, b2) -> {
                if (b1.amount != b2.amount) {
                    return Long.compare(b2.amount, b1.amount);
                }
                return Double.compare(b1.timestamp, b2.timestamp);
            });
            
            Bid winnerBid = sortedBids.get(0);
            auction.winnerId = winnerBid.bidderId;
            
            if (auction.policy == BidPolicy.ENGLISH_PROXY) {
                long secondHighest = -1;
                for (Bid b : auction.bids) {
                    if (!b.bidderId.equals(winnerBid.bidderId)) {
                        if (b.amount > secondHighest) {
                            secondHighest = b.amount;
                        }
                    }
                }
                if (secondHighest != -1) {
                    auction.winningPrice = Math.min(winnerBid.amount, secondHighest + auction.minIncrement);
                } else {
                    auction.winningPrice = auction.startPrice;
                }
            } else if (auction.policy == BidPolicy.VICKREY) {
                long secondHighest = -1;
                for (Bid b : sortedBids) {
                    if (!b.bidderId.equals(winnerBid.bidderId)) {
                        secondHighest = b.amount;
                        break;
                    }
                }
                if (secondHighest != -1) {
                    auction.winningPrice = secondHighest;
                } else {
                    auction.winningPrice = auction.startPrice;
                }
            }
            
            auction.state = AuctionState.SETTLED;
            return true;
        }
    }
}
// Verified compliance
