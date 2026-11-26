import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for File System
 */
class FileSystemTest {

    @BeforeEach
    void setUp() {
        FileSystem.resetInstance();
    }

    @AfterEach
    void tearDown() {
        FileSystem.resetInstance();
    }

    // ============ FileSystemEntry Tests ============

    @Test
    @DisplayName("File stores content correctly")
    void testFileContent() {
        File file = new File("test.txt", "Hello World");
        assertEquals("Hello World", file.read());
        assertEquals(11, file.getSize());
    }

    @Test
    @DisplayName("File append works correctly")
    void testFileAppend() {
        File file = new File("test.txt", "Hello");
        file.append(" World");
        assertEquals("Hello World", file.read());
    }

    @Test
    @DisplayName("File extension extraction works")
    void testFileExtension() {
        File txt = new File("notes.txt");
        File java = new File("Main.java");
        File noExt = new File("README");
        
        assertEquals("txt", txt.getExtension());
        assertEquals("java", java.getExtension());
        assertEquals("", noExt.getExtension());
    }

    @Test
    @DisplayName("Invalid file name throws exception")
    void testInvalidFileName() {
        assertThrows(IllegalArgumentException.class, () -> new File(""));
        assertThrows(IllegalArgumentException.class, () -> new File(null));
        assertThrows(IllegalArgumentException.class, () -> new File("path/file"));
    }

    // ============ Directory Tests ============

    @Test
    @DisplayName("Directory add and get entry works")
    void testDirectoryAddEntry() {
        Directory dir = new Directory("docs");
        File file = new File("test.txt");
        
        assertTrue(dir.addEntry(file));
        assertEquals(file, dir.getEntry("test.txt"));
        assertTrue(dir.hasEntry("test.txt"));
    }

    @Test
    @DisplayName("Directory prevents duplicate entries")
    void testDirectoryDuplicatePrevention() {
        Directory dir = new Directory("docs");
        File file1 = new File("test.txt");
        File file2 = new File("test.txt");
        
        assertTrue(dir.addEntry(file1));
        assertFalse(dir.addEntry(file2));
    }

    @Test
    @DisplayName("Directory remove entry works")
    void testDirectoryRemoveEntry() {
        Directory dir = new Directory("docs");
        File file = new File("test.txt");
        
        dir.addEntry(file);
        assertTrue(dir.removeEntry("test.txt"));
        assertNull(dir.getEntry("test.txt"));
        assertFalse(dir.removeEntry("nonexistent.txt"));
    }

    @Test
    @DisplayName("Directory size is sum of children")
    void testDirectorySize() {
        Directory dir = new Directory("docs");
        dir.addEntry(new File("a.txt", "1234567890"));
        dir.addEntry(new File("b.txt", "12345"));
        
        assertEquals(15, dir.getSize());
    }

    @Test
    @DisplayName("Directory path is calculated correctly")
    void testDirectoryPath() {
        Directory root = new Directory("home");
        Directory user = new Directory("user");
        Directory docs = new Directory("documents");
        
        root.addEntry(user);
        user.addEntry(docs);
        
        assertEquals("/home", root.getPath());
        assertEquals("/home/user", user.getPath());
        assertEquals("/home/user/documents", docs.getPath());
    }

    // ============ FileSystem Singleton Tests ============

    @Test
    @DisplayName("FileSystem singleton returns same instance")
    void testSingletonInstance() {
        FileSystem fs1 = FileSystem.getInstance();
        FileSystem fs2 = FileSystem.getInstance();
        assertSame(fs1, fs2);
    }

    @Test
    @DisplayName("FileSystem creates file")
    void testCreateFile() {
        FileSystem fs = FileSystem.getInstance();
        File file = fs.createFile("/test.txt", "content");
        
        assertNotNull(file);
        assertEquals("test.txt", file.getName());
        assertEquals("content", file.read());
    }

    @Test
    @DisplayName("FileSystem creates nested directories")
    void testCreateDirectory() {
        FileSystem fs = FileSystem.getInstance();
        Directory dir = fs.createDirectory("/home/user/documents");
        
        assertNotNull(dir);
        assertEquals("documents", dir.getName());
        assertTrue(fs.exists("/home"));
        assertTrue(fs.exists("/home/user"));
    }

    @Test
    @DisplayName("FileSystem resolves paths correctly")
    void testResolvePath() {
        FileSystem fs = FileSystem.getInstance();
        fs.createDirectory("/home/user");
        fs.createFile("/home/user/file.txt");
        
        assertNotNull(fs.resolvePath("/home"));
        assertNotNull(fs.resolvePath("/home/user"));
        assertNotNull(fs.resolvePath("/home/user/file.txt"));
        assertNull(fs.resolvePath("/nonexistent"));
    }

    @Test
    @DisplayName("FileSystem handles relative paths with ..")
    void testRelativePathResolution() {
        FileSystem fs = FileSystem.getInstance();
        fs.createDirectory("/home/user");
        fs.changeDirectory("/home/user");
        
        FileSystemEntry parent = fs.resolvePath("..");
        assertNotNull(parent);
        assertEquals("/home", parent.getPath());
    }

    @Test
    @DisplayName("FileSystem delete works")
    void testDelete() {
        FileSystem fs = FileSystem.getInstance();
        fs.createFile("/test.txt");
        
        assertTrue(fs.exists("/test.txt"));
        assertTrue(fs.delete("/test.txt"));
        assertFalse(fs.exists("/test.txt"));
    }

    @Test
    @DisplayName("FileSystem copy file works")
    void testCopyFile() {
        FileSystem fs = FileSystem.getInstance();
        fs.createFile("/original.txt", "content");
        
        assertTrue(fs.copy("/original.txt", "/copy.txt"));
        assertEquals("content", fs.readFile("/copy.txt"));
        assertEquals("content", fs.readFile("/original.txt"));
    }

    @Test
    @DisplayName("FileSystem move file works")
    void testMoveFile() {
        FileSystem fs = FileSystem.getInstance();
        fs.createFile("/original.txt", "content");
        fs.createDirectory("/target");
        
        assertTrue(fs.move("/original.txt", "/target/moved.txt"));
        assertFalse(fs.exists("/original.txt"));
        assertEquals("content", fs.readFile("/target/moved.txt"));
    }

    @Test
    @DisplayName("FileSystem copy directory works")
    void testCopyDirectory() {
        FileSystem fs = FileSystem.getInstance();
        fs.createDirectory("/source");
        fs.createFile("/source/file1.txt", "content1");
        fs.createFile("/source/file2.txt", "content2");
        
        assertTrue(fs.copy("/source", "/destination"));
        assertTrue(fs.exists("/source/file1.txt"));
        assertTrue(fs.exists("/destination/file1.txt"));
        assertEquals("content1", fs.readFile("/destination/file1.txt"));
    }

    @Test
    @DisplayName("FileSystem prevents copy into self")
    void testCopyIntoSelfPrevented() {
        FileSystem fs = FileSystem.getInstance();
        fs.createDirectory("/parent/child");
        
        assertFalse(fs.copy("/parent", "/parent/child/copy"));
    }

    @Test
    @DisplayName("FileSystem search by extension works")
    void testSearchByExtension() {
        FileSystem fs = FileSystem.getInstance();
        fs.createFile("/file1.txt", "a");
        fs.createFile("/file2.txt", "b");
        fs.createFile("/file3.md", "c");
        
        var results = fs.findByExtension("/", "txt");
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("FileSystem search by name pattern works")
    void testSearchByName() {
        FileSystem fs = FileSystem.getInstance();
        fs.createFile("/test_one.txt", "a");
        fs.createFile("/test_two.txt", "b");
        fs.createFile("/other.txt", "c");
        
        var results = fs.findByName("/", "test*");
        assertEquals(2, results.size());
    }

    // ============ Integration Tests ============

    @Test
    @DisplayName("Full workflow test")
    void testFullWorkflow() {
        FileSystem fs = FileSystem.getInstance();
        
        // Create structure
        fs.createDirectory("/home/user/documents");
        fs.createDirectory("/home/user/backup");
        fs.createFile("/home/user/documents/notes.txt", "Important notes");
        
        // Copy
        fs.copy("/home/user/documents/notes.txt", "/home/user/backup/notes_backup.txt");
        
        // Verify
        assertEquals("Important notes", fs.readFile("/home/user/documents/notes.txt"));
        assertEquals("Important notes", fs.readFile("/home/user/backup/notes_backup.txt"));
        
        // Modify original
        fs.writeFile("/home/user/documents/notes.txt", "Updated notes");
        
        // Verify independence
        assertEquals("Updated notes", fs.readFile("/home/user/documents/notes.txt"));
        assertEquals("Important notes", fs.readFile("/home/user/backup/notes_backup.txt"));
        
        // Delete
        fs.delete("/home/user/documents");
        assertFalse(fs.exists("/home/user/documents"));
        assertTrue(fs.exists("/home/user/backup/notes_backup.txt"));
    }
}
