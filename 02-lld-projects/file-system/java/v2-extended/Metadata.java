import java.time.LocalDateTime;

/**
 * File System - V2 Extended
 * 
 * Metadata class to track file/directory information.
 */
class Metadata {
    private LocalDateTime createdAt;
    private LocalDateTime modifiedAt;
    private LocalDateTime accessedAt;
    private String owner;

    public Metadata() {
        this.createdAt = LocalDateTime.now();
        this.modifiedAt = LocalDateTime.now();
        this.accessedAt = LocalDateTime.now();
        this.owner = System.getProperty("user.name", "unknown");
    }

    public Metadata(String owner) {
        this();
        this.owner = owner;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getModifiedAt() {
        return modifiedAt;
    }

    public LocalDateTime getAccessedAt() {
        return accessedAt;
    }

    public String getOwner() {
        return owner;
    }

    public void setOwner(String owner) {
        this.owner = owner;
    }

    public void updateModified() {
        this.modifiedAt = LocalDateTime.now();
    }

    public void updateAccessed() {
        this.accessedAt = LocalDateTime.now();
    }

    /**
     * Create a copy of this metadata with new timestamps.
     */
    public Metadata copy() {
        Metadata copy = new Metadata();
        copy.owner = this.owner;
        return copy;
    }

    @Override
    public String toString() {
        return String.format("Metadata{owner=%s, created=%s, modified=%s}", 
                           owner, createdAt, modifiedAt);
    }
}
