public class PasteMetadata {
    private final long id;
    private final String shortLink;
    private final long createdAtMs;
    private final Long expiresAtMs;

    public PasteMetadata(long id, String shortLink, long createdAtMs, Long expiresAtMs) {
        this.id = id;
        this.shortLink = shortLink;
        this.createdAtMs = createdAtMs;
        this.expiresAtMs = expiresAtMs;
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
}