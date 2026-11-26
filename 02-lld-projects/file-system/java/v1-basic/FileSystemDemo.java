/**
 * File System - V1 Basic
 * 
 * Demo class showing usage of the file system.
 */
public class FileSystemDemo {
    public static void main(String[] args) {
        System.out.println("=== File System Demo ===\n");

        // Get file system instance
        FileSystem fs = FileSystem.getInstance();

        // Create directory structure
        System.out.println("Creating directories...");
        fs.createDirectory("/home");
        fs.createDirectory("/home/user");
        fs.createDirectory("/home/user/documents");
        fs.createDirectory("/home/user/downloads");

        // Create files
        System.out.println("Creating files...");
        fs.createFile("/home/user/documents/notes.txt", "Hello, this is a note!");
        fs.createFile("/home/user/documents/readme.md", "# Readme\nThis is a readme file.");
        fs.createFile("/home/user/downloads/image.png", "binary content here");

        // Display tree
        System.out.println("\nFile System Tree:");
        fs.displayTree();

        // Read file
        System.out.println("\n--- Reading file ---");
        String content = fs.readFile("/home/user/documents/notes.txt");
        System.out.println("Content: " + content);

        // Write to file
        System.out.println("\n--- Writing to file ---");
        fs.writeFile("/home/user/documents/notes.txt", "Updated content!");
        System.out.println("New content: " + fs.readFile("/home/user/documents/notes.txt"));

        // List directory
        System.out.println("\n--- Listing directory ---");
        System.out.println("Contents of /home/user:");
        for (FileSystemEntry entry : fs.list("/home/user")) {
            System.out.println("  " + entry);
        }

        // Navigate with cd
        System.out.println("\n--- Navigation ---");
        fs.changeDirectory("/home/user/documents");
        System.out.println("Current directory: " + fs.getCurrentDirectory().getPath());

        // Resolve relative path
        FileSystemEntry file = fs.resolvePath("notes.txt");
        System.out.println("Resolved 'notes.txt': " + (file != null ? file.getPath() : "null"));

        // Go back with ..
        fs.changeDirectory("..");
        System.out.println("After 'cd ..': " + fs.getCurrentDirectory().getPath());

        // Get file info
        System.out.println("\n--- File Info ---");
        File noteFile = (File) fs.resolvePath("/home/user/documents/notes.txt");
        if (noteFile != null) {
            System.out.println("Name: " + noteFile.getName());
            System.out.println("Path: " + noteFile.getPath());
            System.out.println("Size: " + noteFile.getSize() + " bytes");
            System.out.println("Extension: " + noteFile.getExtension());
            System.out.println("Created: " + noteFile.getCreatedAt());
            System.out.println("Modified: " + noteFile.getModifiedAt());
        }

        // Get directory info
        System.out.println("\n--- Directory Info ---");
        Directory docs = (Directory) fs.resolvePath("/home/user/documents");
        if (docs != null) {
            System.out.println("Name: " + docs.getName());
            System.out.println("Path: " + docs.getPath());
            System.out.println("Total Size: " + docs.getSize() + " bytes");
            System.out.println("Children: " + docs.getChildCount());
        }

        // Delete file
        System.out.println("\n--- Deleting file ---");
        fs.delete("/home/user/downloads/image.png");
        System.out.println("Downloads after delete:");
        for (FileSystemEntry entry : fs.list("/home/user/downloads")) {
            System.out.println("  " + entry);
        }
        System.out.println("(empty)");

        // Delete directory
        System.out.println("\n--- Deleting directory ---");
        fs.delete("/home/user/downloads");
        System.out.println("\nFinal tree:");
        fs.displayTree();

        // Cleanup
        FileSystem.resetInstance();
        System.out.println("\n=== Demo Complete ===");
    }
}
