"""
File System - V1 Basic

Demo script showing usage of the file system.
"""
from file_system import FileSystem


def main():
    print("=== File System Demo ===\n")
    
    # Get file system instance
    fs = FileSystem.get_instance()
    
    # Create directory structure
    print("Creating directories...")
    fs.create_directory("/home")
    fs.create_directory("/home/user")
    fs.create_directory("/home/user/documents")
    fs.create_directory("/home/user/downloads")
    
    # Create files
    print("Creating files...")
    fs.create_file("/home/user/documents/notes.txt", "Hello, this is a note!")
    fs.create_file("/home/user/documents/readme.md", "# Readme\nThis is a readme file.")
    fs.create_file("/home/user/downloads/image.png", "binary content here")
    
    # Display tree
    print("\nFile System Tree:")
    fs.display_tree()
    
    # Read file
    print("\n--- Reading file ---")
    content = fs.read_file("/home/user/documents/notes.txt")
    print(f"Content: {content}")
    
    # Write to file
    print("\n--- Writing to file ---")
    fs.write_file("/home/user/documents/notes.txt", "Updated content!")
    print(f"New content: {fs.read_file('/home/user/documents/notes.txt')}")
    
    # List directory
    print("\n--- Listing directory ---")
    print("Contents of /home/user:")
    for entry in fs.list("/home/user"):
        print(f"  {entry}")
    
    # Navigate with cd
    print("\n--- Navigation ---")
    fs.change_directory("/home/user/documents")
    print(f"Current directory: {fs.current_directory.path}")
    
    # Resolve relative path
    file = fs.resolve_path("notes.txt")
    print(f"Resolved 'notes.txt': {file.path if file else 'null'}")
    
    # Go back with ..
    fs.change_directory("..")
    print(f"After 'cd ..': {fs.current_directory.path}")
    
    # Get file info
    print("\n--- File Info ---")
    note_file = fs.resolve_path("/home/user/documents/notes.txt")
    if note_file:
        print(f"Name: {note_file.name}")
        print(f"Path: {note_file.path}")
        print(f"Size: {note_file.get_size()} bytes")
        print(f"Extension: {note_file.get_extension()}")
        print(f"Created: {note_file.created_at}")
        print(f"Modified: {note_file.modified_at}")
    
    # Get directory info
    print("\n--- Directory Info ---")
    docs = fs.resolve_path("/home/user/documents")
    if docs:
        print(f"Name: {docs.name}")
        print(f"Path: {docs.path}")
        print(f"Total Size: {docs.get_size()} bytes")
        print(f"Children: {docs.get_child_count()}")
    
    # Delete file
    print("\n--- Deleting file ---")
    fs.delete("/home/user/downloads/image.png")
    print("Downloads after delete:")
    entries = fs.list("/home/user/downloads")
    if not entries:
        print("  (empty)")
    
    # Delete directory
    print("\n--- Deleting directory ---")
    fs.delete("/home/user/downloads")
    
    print("\nFinal tree:")
    fs.display_tree()
    
    # Cleanup
    FileSystem.reset_instance()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
