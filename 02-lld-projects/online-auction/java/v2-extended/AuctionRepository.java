import java.util.Optional;

public interface AuctionRepository {
    void save(String auctionId, String payload);
    Optional<String> find(String auctionId);
}
