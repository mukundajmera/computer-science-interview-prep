import java.util.*;

/**
 * File System - V1 Basic
 * 
 * Main FileSystem class implementing Singleton pattern.
 * Manages root directory and provides path-based operations.
 */
class FileSystem {
    private static FileSystem instance;
    
    private final Directory root;
    private Directory currentDirectory;

    /**
     * Private constructor for Singleton.
     */
    private FileSystem() {
        // Root directory has special name
        this.root = new Directory("") {
            @Override
            public String getPath() {
                return "/";
            }
        };
        this.currentDirectory = root;
    }

    /**
     * Get the singleton instance.
     */
    public static synchronized FileSystem getInstance() {
        if (instance == null) {
            instance = new FileSystem();
        }
        return instance;
    }

    /**
     * Reset the singleton (for testing only).
     */
    public static synchronized void resetInstance() {
        instance = null;
    }

    /**
     * Get the root directory.
     */
    public Directory getRoot() {
        return root;
    }

    /**
     * Get current working directory.
     */
    public Directory getCurrentDirectory() {
        return currentDirectory;
    }

    /**
     * Change current directory.
     */
    public boolean changeDirectory(String path) {
        FileSystemEntry entry = resolvePath(path);
        if (entry != null && entry.isDirectory()) {
            currentDirectory = (Directory) entry;
            return true;
        }
        return false;
    }

    /**
     * Create a file at the given path.
     */
    public File createFile(String path) {
        return createFile(path, "");
    }

    /**
     * Create a file at the given path with content.
     */
    public File createFile(String path, String content) {
        if (path == null || path.isEmpty()) {
            throw new IllegalArgumentException("Path cannot be null or empty");
        }

        // Parse path to get parent directory path and file name
        String[] parts = parsePath(path);
        String parentPath = parts[0];
        String fileName = parts[1];

        // Get or create parent directory
        Directory parent = getOrCreateDirectory(parentPath);
        if (parent == null) {
            System.out.println("Cannot create parent directory: " + parentPath);
            return null;
        }

        // Check if file already exists
        if (parent.hasEntry(fileName)) {
            System.out.println("Entry already exists: " + fileName);
            return null;
        }

        // Create and add file
        File file = new File(fileName, content);
        parent.addEntry(file);
        return file;
    }

    /**
     * Create a directory at the given path.
     */
    public Directory createDirectory(String path) {
        if (path == null || path.isEmpty() || path.equals("/")) {
            throw new IllegalArgumentException("Invalid path");
        }

        // Parse path
        String[] parts = parsePath(path);
        String parentPath = parts[0];
        String dirName = parts[1];

        // Get or create parent directory
        Directory parent = getOrCreateDirectory(parentPath);
        if (parent == null) {
            System.out.println("Cannot create parent directory: " + parentPath);
            return null;
        }

        // Check if already exists
        if (parent.hasEntry(dirName)) {
            FileSystemEntry existing = parent.getEntry(dirName);
            if (existing.isDirectory()) {
                return (Directory) existing;
            }
            System.out.println("File exists with same name: " + dirName);
            return null;
        }

        // Create and add directory
        Directory dir = new Directory(dirName);
        parent.addEntry(dir);
        return dir;
    }

    /**
     * Get or create directory at path (like mkdir -p).
     */
    private Directory getOrCreateDirectory(String path) {
        if (path == null || path.isEmpty() || path.equals("/")) {
            return root;
        }

        String[] components = getPathComponents(path);
        Directory current = root;

        for (String component : components) {
            if (component.isEmpty()) continue;
            
            FileSystemEntry entry = current.getEntry(component);
            if (entry == null) {
                // Create directory
                Directory newDir = new Directory(component);
                current.addEntry(newDir);
                current = newDir;
            } else if (entry.isDirectory()) {
                current = (Directory) entry;
            } else {
                // File exists with same name
                return null;
            }
        }
        return current;
    }

    /**
     * Delete entry at path.
     */
    public boolean delete(String path) {
        if (path == null || path.isEmpty() || path.equals("/")) {
            System.out.println("Cannot delete root directory");
            return false;
        }

        FileSystemEntry entry = resolvePath(path);
        if (entry == null) {
            System.out.println("Path not found: " + path);
            return false;
        }

        return entry.delete();
    }

    /**
     * List contents of directory at path.
     */
    public List<FileSystemEntry> list(String path) {
        FileSystemEntry entry = resolvePath(path);
        if (entry == null) {
            System.out.println("Path not found: " + path);
            return Collections.emptyList();
        }
        if (!entry.isDirectory()) {
            return Collections.singletonList(entry);
        }
        return ((Directory) entry).listEntries();
    }

    /**
     * Read file content.
     */
    public String readFile(String path) {
        FileSystemEntry entry = resolvePath(path);
        if (entry == null) {
            System.out.println("File not found: " + path);
            return null;
        }
        if (!entry.isFile()) {
            System.out.println("Not a file: " + path);
            return null;
        }
        return ((File) entry).read();
    }

    /**
     * Write content to file.
     */
    public boolean writeFile(String path, String content) {
        FileSystemEntry entry = resolvePath(path);
        if (entry == null) {
            // Create file if doesn't exist
            File file = createFile(path, content);
            return file != null;
        }
        if (!entry.isFile()) {
            System.out.println("Not a file: " + path);
            return false;
        }
        ((File) entry).write(content);
        return true;
    }

    /**
     * Resolve a path to a FileSystemEntry.
     */
    public FileSystemEntry resolvePath(String path) {
        if (path == null || path.isEmpty()) {
            return currentDirectory;
        }
        
        // Absolute path starts with /
        Directory start = path.startsWith("/") ? root : currentDirectory;
        
        if (path.equals("/")) {
            return root;
        }

        String[] components = getPathComponents(path);
        FileSystemEntry current = start;

        for (String component : components) {
            if (component.isEmpty() || component.equals(".")) {
                continue;
            }
            
            if (component.equals("..")) {
                if (current.getParent() != null) {
                    current = current.getParent();
                }
                continue;
            }

            if (!current.isDirectory()) {
                return null;
            }

            FileSystemEntry next = ((Directory) current).getEntry(component);
            if (next == null) {
                return null;
            }
            current = next;
        }

        return current;
    }

    /**
     * Check if path exists.
     */
    public boolean exists(String path) {
        return resolvePath(path) != null;
    }

    /**
     * Parse path into parent path and entry name.
     */
    private String[] parsePath(String path) {
        // Remove trailing slash
        if (path.endsWith("/") && path.length() > 1) {
            path = path.substring(0, path.length() - 1);
        }
        
        int lastSlash = path.lastIndexOf('/');
        String parentPath;
        String name;
        
        if (lastSlash == -1) {
            // Relative path with just name
            parentPath = "";
            name = path;
        } else if (lastSlash == 0) {
            // Root level
            parentPath = "/";
            name = path.substring(1);
        } else {
            parentPath = path.substring(0, lastSlash);
            name = path.substring(lastSlash + 1);
        }
        
        return new String[]{parentPath, name};
    }

    /**
     * Split path into components.
     */
    private String[] getPathComponents(String path) {
        if (path.startsWith("/")) {
            path = path.substring(1);
        }
        if (path.endsWith("/")) {
            path = path.substring(0, path.length() - 1);
        }
        if (path.isEmpty()) {
            return new String[0];
        }
        return path.split("/");
    }

    /**
     * Display the file system tree.
     */
    public void displayTree() {
        System.out.println("/");
        for (FileSystemEntry entry : root.listEntries()) {
            if (entry.isDirectory()) {
                ((Directory) entry).displayTree("  ");
            } else {
                System.out.println("  " + entry);
            }
        }
    }
}
