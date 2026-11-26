/**
 * File System - V3 Optimized
 * 
 * SearchCriteria class (same as v2).
 */
class SearchCriteria {
    private String namePattern;
    private String extension;
    private Long minSize;
    private Long maxSize;
    private boolean filesOnly;
    private boolean directoriesOnly;

    public SearchCriteria() {
    }

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

    public boolean matches(FileSystemEntry entry) {
        if (filesOnly && !entry.isFile()) {
            return false;
        }
        if (directoriesOnly && !entry.isDirectory()) {
            return false;
        }

        if (namePattern != null && !matchesPattern(entry.getName(), namePattern)) {
            return false;
        }

        if (extension != null) {
            if (!entry.isFile()) {
                return false;
            }
            File file = (File) entry;
            if (!extension.equalsIgnoreCase(file.getExtension())) {
                return false;
            }
        }

        long size = entry.getSize();
        if (minSize != null && size < minSize) {
            return false;
        }
        if (maxSize != null && size > maxSize) {
            return false;
        }

        return true;
    }

    private boolean matchesPattern(String name, String pattern) {
        String regex = pattern
            .replace(".", "\\.")
            .replace("*", ".*")
            .replace("?", ".");
        return name.matches(regex);
    }
}
