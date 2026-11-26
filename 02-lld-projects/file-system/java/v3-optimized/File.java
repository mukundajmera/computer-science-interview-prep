/**
 * File System - V1 Basic
 * 
 * File class (Composite Leaf) - stores content and metadata.
 */
class File extends FileSystemEntry {
    private String content;

    public File(String name) {
        super(name);
        this.content = "";
    }

    public File(String name, String content) {
        super(name);
        this.content = content != null ? content : "";
    }

    /**
     * Read the file content.
     */
    public String read() {
        return content;
    }

    /**
     * Write content to the file (overwrites existing content).
     */
    public void write(String content) {
        this.content = content != null ? content : "";
        updateModified();
    }

    /**
     * Append content to the file.
     */
    public void append(String content) {
        if (content != null) {
            this.content += content;
            updateModified();
        }
    }

    /**
     * Get the file size (content length).
     */
    @Override
    public long getSize() {
        return content.length();
    }

    @Override
    public boolean isFile() {
        return true;
    }

    @Override
    public boolean isDirectory() {
        return false;
    }

    /**
     * Get the file extension (e.g., "txt" from "file.txt").
     */
    public String getExtension() {
        int dotIndex = name.lastIndexOf('.');
        if (dotIndex > 0 && dotIndex < name.length() - 1) {
            return name.substring(dotIndex + 1);
        }
        return "";
    }

    @Override
    public String toString() {
        return "[F] " + name + " (" + getSize() + " bytes)";
    }
}
