/**
 * File System - V2 Extended
 * 
 * SearchCriteria class for flexible file searching.
 * Uses builder pattern for fluent API.
 */
class SearchCriteria {
    private String namePattern;    // Simple pattern matching with * wildcard
    private String extension;      // File extension (without dot)
    private Long minSize;          // Minimum size in bytes
    private Long maxSize;          // Maximum size in bytes
    private boolean filesOnly;     // Search only files
    private boolean directoriesOnly; // Search only directories

    public SearchCriteria() {
    }

    // Builder methods
    public SearchCriteria withName(String pattern) {
        this.namePattern = pattern;
        return this;
    }

    public SearchCriteria withExtension(String ext) {
        this.extension = ext;
        return this;
    }

    public SearchCriteria withMinSize(long minSize) {
        this.minSize = minSize;
        return this;
    }

    public SearchCriteria withMaxSize(long maxSize) {
        this.maxSize = maxSize;
        return this;
    }

    public SearchCriteria withSizeRange(long min, long max) {
        this.minSize = min;
        this.maxSize = max;
        return this;
    }

    public SearchCriteria filesOnly() {
        this.filesOnly = true;
        this.directoriesOnly = false;
        return this;
    }

    public SearchCriteria directoriesOnly() {
        this.directoriesOnly = true;
        this.filesOnly = false;
        return this;
    }

    /**
     * Check if an entry matches all specified criteria.
     */
    public boolean matches(FileSystemEntry entry) {
        // Type check
        if (filesOnly && !entry.isFile()) {
            return false;
        }
        if (directoriesOnly && !entry.isDirectory()) {
            return false;
        }

        // Name pattern check
        if (namePattern != null && !matchesPattern(entry.getName(), namePattern)) {
            return false;
        }

        // Extension check (only for files)
        if (extension != null) {
            if (!entry.isFile()) {
                return false;
            }
            File file = (File) entry;
            if (!extension.equalsIgnoreCase(file.getExtension())) {
                return false;
            }
        }

        // Size checks
        long size = entry.getSize();
        if (minSize != null && size < minSize) {
            return false;
        }
        if (maxSize != null && size > maxSize) {
            return false;
        }

        return true;
    }

    /**
     * Simple pattern matching with * wildcard.
     */
    private boolean matchesPattern(String name, String pattern) {
        // Convert glob pattern to regex
        String regex = pattern
            .replace(".", "\\.")
            .replace("*", ".*")
            .replace("?", ".");
        return name.matches(regex);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("SearchCriteria{");
        if (namePattern != null) sb.append("name=").append(namePattern).append(", ");
        if (extension != null) sb.append("ext=").append(extension).append(", ");
        if (minSize != null) sb.append("minSize=").append(minSize).append(", ");
        if (maxSize != null) sb.append("maxSize=").append(maxSize).append(", ");
        if (filesOnly) sb.append("filesOnly, ");
        if (directoriesOnly) sb.append("directoriesOnly, ");
        sb.append("}");
        return sb.toString();
    }
}
