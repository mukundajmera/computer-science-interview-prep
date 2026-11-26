import java.time.LocalDateTime;

/**
 * File System - V3 Optimized
 * 
 * Metadata class with enhanced tracking.
 */
class Metadata {
    private LocalDateTime createdAt;
    private LocalDateTime modifiedAt;
    private LocalDateTime accessedAt;
    private String owner;
    private String group;

    public Metadata() {
        this.createdAt = LocalDateTime.now();
        this.modifiedAt = LocalDateTime.now();
        this.accessedAt = LocalDateTime.now();
        this.owner = System.getProperty("user.name", "unknown");
        this.group = "users";
    }

    public Metadata(String owner, String group) {
        this();
        this.owner = owner;
        this.group = group;
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

    public String getGroup() {
        return group;
    }

    public void setOwner(String owner) {
        this.owner = owner;
    }

    public void setGroup(String group) {
        this.group = group;
    }

    public void updateModified() {
        this.modifiedAt = LocalDateTime.now();
    }

    public void updateAccessed() {
        this.accessedAt = LocalDateTime.now();
    }

    public Metadata copy() {
        Metadata copy = new Metadata();
        copy.owner = this.owner;
        copy.group = this.group;
        return copy;
    }

    @Override
    public String toString() {
        return String.format("Metadata{owner=%s, group=%s, created=%s}", 
                           owner, group, createdAt);
    }
}
