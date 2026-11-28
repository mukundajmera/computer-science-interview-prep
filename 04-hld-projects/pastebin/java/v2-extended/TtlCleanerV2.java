import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReadWriteLock;

/**
 * v2 TTL cleaner: like v1 but returns the swept links so the service can
 * purge its read cache (improvement #2 hygiene).
 * See PastebinServiceV2 for the full v2 list.
 */
public class TtlCleanerV2 {

    private final Map<String, PasteMetadataV2> metadataStore;
    private final Map<String, String> blobStore;
    private final ReadWriteLock lock;

    public TtlCleanerV2(Map<String, PasteMetadataV2> metadataStore, Map<String, String> blobStore, ReadWriteLock lock) {
        this.metadataStore = metadataStore;
        this.blobStore = blobStore;
        this.lock = lock;
    }

    public List<String> sweep() {
        long now = System.currentTimeMillis();
        List<String> expiredLinks = new ArrayList<>();

        lock.writeLock().lock();
        try {
            for (Map.Entry<String, PasteMetadataV2> entry : metadataStore.entrySet()) {
                Long expiresAt = entry.getValue().getExpiresAtMs();
                if (expiresAt != null && now > expiresAt) {
                    expiredLinks.add(entry.getKey());
                }
            }

            for (String shortLink : expiredLinks) {
                metadataStore.remove(shortLink);
                blobStore.remove(shortLink);
            }
        } finally {
            lock.writeLock().unlock();
        }

        return expiredLinks;
    }
}
