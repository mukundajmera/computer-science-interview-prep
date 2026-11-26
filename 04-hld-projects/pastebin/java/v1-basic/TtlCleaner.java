import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReadWriteLock;

public class TtlCleaner {
    
    private final Map<String, PasteMetadata> metadataStore;
    private final Map<String, String> blobStore;
    private final ReadWriteLock lock;

    public TtlCleaner(Map<String, PasteMetadata> metadataStore, Map<String, String> blobStore, ReadWriteLock lock) {
        this.metadataStore = metadataStore;
        this.blobStore = blobStore;
        this.lock = lock;
    }

    public int sweep() {
        long now = System.currentTimeMillis();
        List<String> expiredLinks = new ArrayList<>();

        lock.writeLock().lock();
        try {
            for (Map.Entry<String, PasteMetadata> entry : metadataStore.entrySet()) {
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
        
        return expiredLinks.size();
    }
}