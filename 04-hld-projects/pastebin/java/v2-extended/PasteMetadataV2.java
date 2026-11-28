/**
 * v2 paste metadata: v1 fields plus burnAfterReading (improvement #1).
 * See PastebinServiceV2 for the full v2 list.
 */
public class PasteMetadataV2 {
    private final long id;
    private final String shortLink;
    private final long createdAtMs;
    private final Long expiresAtMs;
    private final boolean burnAfterReading;

    public PasteMetadataV2(long id, String shortLink, long createdAtMs, Long expiresAtMs, boolean burnAfterReading) {
        this.id = id;
        this.shortLink = shortLink;
        this.createdAtMs = createdAtMs;
        this.expiresAtMs = expiresAtMs;
        this.burnAfterReading = burnAfterReading;
    }

    public long getId() {
        return id;
    }

    public String getShortLink() {
        return shortLink;
    }

    public long getCreatedAtMs() {
        return createdAtMs;
    }

    public Long getExpiresAtMs() {
        return expiresAtMs;
    }

    public boolean isBurnAfterReading() {
        return burnAfterReading;
    }
}
