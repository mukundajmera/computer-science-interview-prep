import java.time.LocalDateTime;
import java.util.*;

/**
 * File System - V1 Basic
 * 
 * Abstract base class for file system entries using Composite pattern.
 * Both File and Directory extend this class.
 */
abstract class FileSystemEntry {
    protected String name;
    protected Directory parent;
    protected LocalDateTime createdAt;
    protected LocalDateTime modifiedAt;

    public FileSystemEntry(String name) {
        validateName(name);
        this.name = name;
        this.parent = null;
        this.createdAt = LocalDateTime.now();
        this.modifiedAt = LocalDateTime.now();
    }

    private void validateName(String name) {
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("Name cannot be null or empty");
        }
        if (name.contains("/") || name.contains("\\")) {
            throw new IllegalArgumentException("Name cannot contain path separators");
        }
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        validateName(name);
        this.name = name;
        updateModified();
    }

    public Directory getParent() {
        return parent;
    }

    protected void setParent(Directory parent) {
        this.parent = parent;
    }

    public String getPath() {
        if (parent == null) {
            return "/" + name;
        }
        String parentPath = parent.getPath();
        if (parentPath.equals("/")) {
            return "/" + name;
        }
        return parentPath + "/" + name;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getModifiedAt() {
        return modifiedAt;
    }

    protected void updateModified() {
        this.modifiedAt = LocalDateTime.now();
    }

    public abstract long getSize();
    public abstract boolean isFile();
    public abstract boolean isDirectory();

    /**
     * Delete this entry from its parent.
     */
    public boolean delete() {
        if (parent != null) {
            return parent.removeEntry(name);
        }
        return false;
    }

    @Override
    public String toString() {
        return (isDirectory() ? "[D] " : "[F] ") + name;
    }
}
