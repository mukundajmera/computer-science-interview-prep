import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.List;
import java.util.ArrayList;

public class AuctionServiceV2 implements BidService {
    private final AuctionRepository repository;
    final Map<String, Auction> auctions = new HashMap<>();
    private final Map<BidPolicy, BidValidationPolicy> policies = new HashMap<>();
    private final Object lock = new Object();

    public AuctionServiceV2(AuctionRepository repository) {
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

    @Override
    public boolean placeBid(String auctionId, String bidderId, long amount, String idempotencyKey, double currentTime) {
        if (amount <= 0) {
            return false;
        }
        
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction == null || auction.state != AuctionState.OPEN || currentTime > auction.endTime || bidderId.equals(auction.sellerId)) {
                return false;
            }
            
            if (idempotencyKey != null && !idempotencyKey.isEmpty()) {
                for (Bid bid : auction.bids) {
                    if (idempotencyKey.equals(bid.idempotencyKey)) {
                        return true;
                    }
                }
            }
            
            BidValidationPolicy policyImpl = policies.get(auction.policy);
            if (policyImpl == null) {
                return false;
            }
            
            long highestBid = auction.startPrice - auction.minIncrement;
            if (auction.policy == BidPolicy.ENGLISH_PROXY && !auction.bids.isEmpty()) {
                for (Bid b : auction.bids) {
                    if (b.amount > highestBid) {
                        highestBid = b.amount;
                    }
                }
            }
            
            if (!policyImpl.isValidBid(highestBid, amount, auction.state, auction)) {
                return false;
            }
            
            auction.bids.add(new Bid(bidderId, amount, currentTime, idempotencyKey));
            
            double timeLeft = auction.endTime - currentTime;
            if (timeLeft <= auction.extensionWindow && auction.extensionCount < auction.extensionLimit) {
                auction.endTime += auction.extensionDuration;
                auction.extensionCount++;
            }
            
            return true;
        }
    }
    
    public boolean settleAuction(String auctionId, double currentTime) {
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction == null || currentTime <= auction.endTime) {
                return false;
            }
            if (auction.state == AuctionState.SETTLED) {
                return true;
            }
            
            auction.state = AuctionState.CLOSED;
            
            if (auction.bids.isEmpty()) {
                auction.state = AuctionState.SETTLED;
                return true;
            }
            
            List<Bid> sortedBids = new ArrayList<>(auction.bids);
            sortedBids.sort((b1, b2) -> b1.amount != b2.amount ? Long.compare(b2.amount, b1.amount) : Double.compare(b1.timestamp, b2.timestamp));
            
            Bid winnerBid = sortedBids.get(0);
            auction.winnerId = winnerBid.bidderId;
            
            if (auction.policy == BidPolicy.ENGLISH_PROXY) {
                long secondHighest = -1;
                for (Bid b : auction.bids) {
                    if (!b.bidderId.equals(winnerBid.bidderId) && b.amount > secondHighest) {
                        secondHighest = b.amount;
                    }
                }
                auction.winningPrice = secondHighest != -1 ? Math.min(winnerBid.amount, secondHighest + auction.minIncrement) : auction.startPrice;
            } else if (auction.policy == BidPolicy.VICKREY) {
                long secondHighest = -1;
                for (Bid b : sortedBids) {
                    if (!b.bidderId.equals(winnerBid.bidderId)) {
                        secondHighest = b.amount;
                        break;
                    }
                }
                auction.winningPrice = secondHighest != -1 ? secondHighest : auction.startPrice;
            }
            
            auction.state = AuctionState.SETTLED;
            return true;
        }
    }
}
