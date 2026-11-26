package v3_optimized;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v3_optimized.UnixVfs;
import v3_optimized.UnixVfs.FileDescriptor;
import v3_optimized.UnixVfs.Inode;
public class UnixVfsTest {

    @Test
    public void testNormalUseCase() {
        UnixVfs vfs = new UnixVfs();
        vfs.mkdir("/dir1", 0755);
        vfs.create("/dir1/file1", 0755);

        FileDescriptor fd = vfs.open("/dir1/file1", "w");
        vfs.write(fd, "test data".getBytes());
        

        FileDescriptor fd2 = vfs.open("/dir1/file1", "r");
        byte[] data = vfs.read(fd2, 9);
        

        assertArrayEquals("test data".getBytes(), data);
    }

    @Test
    public void testEmptyInvalidInput() {
        UnixVfs vfs = new UnixVfs();
        assertFalse(vfs.create("", 0755));
        assertFalse(vfs.create(null, 0755));
        assertFalse(vfs.create("invalid", 0755));
        assertFalse(vfs.mkdir("", 0755));
    }

    @Test
    public void testDuplicateOperation() {
        UnixVfs vfs = new UnixVfs();
        vfs.mkdir("/dir1", 0755);
        assertTrue(vfs.create("/dir1/file1", 0755));
        assertFalse(vfs.create("/dir1/file1", 0755));
    }

    @Test
    public void testCapacityBoundary() {
        UnixVfs vfs = new UnixVfs();
        vfs.symlink("/link2", "/link1");
        vfs.symlink("/link1", "/link2");

        assertThrows(RuntimeException.class, () -> {
            vfs.stat("/link1");
        });
    }

    @Test
    public void testFailureRollback() {
        UnixVfs vfs = new UnixVfs();
        vfs.mkdir("/dir1", 0755);
        vfs.create("/dir1/file1", 0755);
        
        // Link to non-existent directory shouldn't leave partial state
        assertFalse(vfs.link("/dir1/file1", "/missing/file2"));
        Inode inode = vfs.stat("/dir1/file1");
        assertEquals(1, inode.getLinkCount());
    }
}
