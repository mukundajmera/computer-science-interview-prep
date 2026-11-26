import java.util.*;

/**
 * File System - V1 Basic
 * 
 * Directory class (Composite Composite) - contains files and subdirectories.
 */
class Directory extends FileSystemEntry {
    private final Map<String, FileSystemEntry> children;

    public Directory(String name) {
        super(name);
        this.children = new HashMap<>();
    }

    /**
     * Add an entry to this directory.
     */
    public boolean addEntry(FileSystemEntry entry) {
        if (entry == null) {
            throw new IllegalArgumentException("Entry cannot be null");
        }
        if (children.containsKey(entry.getName())) {
            return false; // Entry with same name already exists
        }
        
        // Remove from old parent if exists
        if (entry.getParent() != null) {
            entry.getParent().removeEntry(entry.getName());
        }
        
        children.put(entry.getName(), entry);
        entry.setParent(this);
        updateModified();
        return true;
    }

    /**
     * Remove an entry by name.
     */
    public boolean removeEntry(String name) {
        FileSystemEntry entry = children.remove(name);
        if (entry != null) {
            entry.setParent(null);
            updateModified();
            return true;
        }
        return false;
    }

    /**
     * Get an entry by name.
     */
    public FileSystemEntry getEntry(String name) {
        return children.get(name);
    }

    /**
     * Check if directory contains an entry with given name.
     */
    public boolean hasEntry(String name) {
        return children.containsKey(name);
    }

    /**
     * List all entries in this directory.
     */
    public List<FileSystemEntry> listEntries() {
        return new ArrayList<>(children.values());
    }

    /**
     * List only files in this directory.
     */
    public List<File> listFiles() {
        List<File> files = new ArrayList<>();
        for (FileSystemEntry entry : children.values()) {
            if (entry.isFile()) {
                files.add((File) entry);
            }
        }
        return files;
    }

    /**
     * List only subdirectories.
     */
    public List<Directory> listDirectories() {
        List<Directory> directories = new ArrayList<>();
        for (FileSystemEntry entry : children.values()) {
            if (entry.isDirectory()) {
                directories.add((Directory) entry);
            }
        }
        return directories;
    }

    /**
     * Get the total size of this directory (sum of all children).
     */
    @Override
    public long getSize() {
        long totalSize = 0;
        for (FileSystemEntry entry : children.values()) {
            totalSize += entry.getSize();
        }
        return totalSize;
    }

    /**
     * Get the number of direct children.
     */
    public int getChildCount() {
        return children.size();
    }

    /**
     * Check if directory is empty.
     */
    public boolean isEmpty() {
        return children.isEmpty();
    }

    @Override
    public boolean isFile() {
        return false;
    }

    @Override
    public boolean isDirectory() {
        return true;
    }

    /**
     * Delete this directory and all its contents recursively.
     */
    @Override
    public boolean delete() {
        // First delete all children
        for (FileSystemEntry entry : new ArrayList<>(children.values())) {
            if (entry.isDirectory()) {
                ((Directory) entry).delete();
            }
            children.remove(entry.getName());
        }
        // Then remove from parent
        return super.delete();
    }

    @Override
    public String toString() {
        return "[D] " + name + " (" + children.size() + " items)";
    }

    /**
     * Display directory tree structure.
     */
    public void displayTree(String indent) {
        System.out.println(indent + toString());
        for (FileSystemEntry entry : children.values()) {
            if (entry.isDirectory()) {
                ((Directory) entry).displayTree(indent + "  ");
            } else {
                System.out.println(indent + "  " + entry);
            }
        }
    }
}
