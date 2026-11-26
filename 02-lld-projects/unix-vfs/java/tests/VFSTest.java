
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.Optional;
import java.lang.reflect.InvocationTargetException;

public class VFSTest {

    private Object createVFS() throws Exception {
        try {
            return Class.forName("v2_extended.UnixVfs").getDeclaredConstructor().newInstance();
        } catch (ClassNotFoundException e) {
            return Class.forName("v1_basic.VFS").getDeclaredConstructor().newInstance();
        }
    }

    private Object invokeMethod(Object obj, String methodName, Object... args) throws Exception {
        Class<?>[] argTypes = new Class<?>[args.length];
        for (int i = 0; i < args.length; i++) {
            if (args[i] instanceof Integer) {
                argTypes[i] = int.class;
            } else if (args[i] instanceof String) {
                argTypes[i] = String.class;
            } else if (args[i] instanceof byte[]) {
                argTypes[i] = byte[].class;
            } else {
                argTypes[i] = args[i].getClass();
            }
        }
        
        // Find method
        Method method = null;
        for (Method m : obj.getClass().getMethods()) {
            if (m.getName().equals(methodName) && m.getParameterTypes().length == args.length) {
                boolean match = true;
                for (int i = 0; i < args.length; i++) {
                    Class<?> paramType = m.getParameterTypes()[i];
                    if (args[i] != null && !paramType.isAssignableFrom(args[i].getClass())) {
                        if (paramType == int.class && args[i] instanceof Integer) continue;
                        if (paramType == byte[].class && args[i] instanceof byte[]) continue;
                        if (paramType.getName().endsWith("FileDescriptor")) continue; // Approximate match
                        match = false;
                    }
                }
                if (match) {
                    method = m;
                    break;
                }
            }
        }
        
        if (method != null) {
            return method.invoke(obj, args);
        }
        throw new NoSuchMethodException(methodName);
    }
    
    private Object getLinkCount(Object inode) throws Exception {
        return inode.getClass().getMethod("getLinkCount").invoke(inode);
    }

    private Object getOpenCount(Object inode) throws Exception {
        try {
            return inode.getClass().getMethod("getOpenCount").invoke(inode);
        } catch (NoSuchMethodException e) {
            return 0;
        }
    }
    
    private Object getPermissions(Object inode) throws Exception {
        return inode.getClass().getMethod("getPermissions").invoke(inode);
    }
    
    private int getInodeId(Object inode) throws Exception {
        return (int) inode.getClass().getMethod("getInodeId").invoke(inode);
    }
    
    private boolean isDirectory(Object inode) throws Exception {
        Object fileType = inode.getClass().getMethod("getFileType").invoke(inode);
        return "DIRECTORY".equals(fileType.toString());
    }

    private int getOffset(Object fd) throws Exception {
        return (int) fd.getClass().getMethod("getOffset").invoke(fd);
    }

    @Test
    public void testHardLinksAndRefCounting() throws Exception {
        Object vfs = createVFS();
        invokeMethod(vfs, "mkdir", "/dir1");
        invokeMethod(vfs, "create", "/dir1/file1");

        Object inode = invokeMethod(vfs, "stat", "/dir1/file1");
        assertNotNull(inode);
        assertEquals(1, (int) getLinkCount(inode));

        invokeMethod(vfs, "mkdir", "/dir2");
        assertTrue((Boolean) invokeMethod(vfs, "link", "/dir1/file1", "/dir2/file2"));

        assertEquals(2, (int) getLinkCount(inode));

        assertTrue((Boolean) invokeMethod(vfs, "unlink", "/dir1/file1"));
        assertEquals(1, (int) getLinkCount(inode));
        assertEquals(inode, invokeMethod(vfs, "stat", "/dir2/file2"));

        assertTrue((Boolean) invokeMethod(vfs, "unlink", "/dir2/file2"));
        assertEquals(0, (int) getLinkCount(inode));
        
        Map<?, ?> inodes = (Map<?, ?>) invokeMethod(vfs, "getInodes");
        assertFalse(inodes.containsKey(getInodeId(inode)));
    }

    @Test
    public void testSymlinkCycleDetection() throws Exception {
        Object vfs = createVFS();
        invokeMethod(vfs, "symlink", "/link2", "/link1");
        invokeMethod(vfs, "symlink", "/link1", "/link2");

        InvocationTargetException exception = assertThrows(InvocationTargetException.class, () -> {
            invokeMethod(vfs, "stat", "/link1");
        });
        assertTrue(exception.getTargetException() instanceof RuntimeException);
        assertEquals("Too many levels of symbolic links", exception.getTargetException().getMessage());
    }

    @Test
    public void testFileDescriptorIndependentCursor() throws Exception {
        Object vfs = createVFS();
        invokeMethod(vfs, "create", "/testfile");

        Object fd1 = invokeMethod(vfs, "open", "/testfile", "w");
        assertNotNull(fd1);
        invokeMethod(vfs, "write", fd1, "Hello, World!".getBytes());

        Object fd2 = invokeMethod(vfs, "open", "/testfile", "r");
        assertNotNull(fd2);
        assertEquals(0, getOffset(fd2));

        byte[] data = (byte[]) invokeMethod(vfs, "read", fd2, 5);
        assertArrayEquals("Hello".getBytes(), data);
        assertEquals(5, getOffset(fd2));

        Object fd3 = invokeMethod(vfs, "open", "/testfile", "r");
        assertNotNull(fd3);
        assertEquals(0, getOffset(fd3));
        byte[] data2 = (byte[]) invokeMethod(vfs, "read", fd3, 5);
        assertArrayEquals("Hello".getBytes(), data2);

        invokeMethod(vfs, "lseek", fd2, 7, 0); // SEEK_SET
        byte[] data3 = (byte[]) invokeMethod(vfs, "read", fd2, 6);
        assertArrayEquals("World!".getBytes(), data3);
        assertEquals(13, getOffset(fd2));
    }

    @Test
    public void testOctalPermissionBitmask() throws Exception {
        Object vfs = createVFS();
        invokeMethod(vfs, "create", "/file1", 0644);
        Object inode = invokeMethod(vfs, "stat", "/file1");
        assertNotNull(inode);
        assertEquals(0644, (int) getPermissions(inode));

        assertTrue((Boolean) invokeMethod(vfs, "chmod", "/file1", 0755));
        assertEquals(0755, (int) getPermissions(inode));
    }
    
    @Test
    public void testErrorCasesAndHierarchy() throws Exception {
        Object vfs = createVFS();
        
        // 1. Directory recursion and path parsing
        assertTrue((Boolean) invokeMethod(vfs, "mkdir", "/a"));
        assertTrue((Boolean) invokeMethod(vfs, "mkdir", "/a/b"));
        assertTrue((Boolean) invokeMethod(vfs, "mkdir", "/a/b/c"));
        assertTrue((Boolean) invokeMethod(vfs, "create", "/a/b/c/file.txt"));
        
        Object inode = invokeMethod(vfs, "stat", "/a/b/c/file.txt");
        assertNotNull(inode);
        assertFalse(isDirectory(inode));
        
        // 2. File not found
        assertNull(invokeMethod(vfs, "stat", "/a/b/c/missing.txt"));
        assertNull(invokeMethod(vfs, "open", "/a/b/c/missing.txt", "r"));
        
        // 3. Not a directory error
        assertFalse((Boolean) invokeMethod(vfs, "create", "/a/b/c/file.txt/nested.txt"));
        assertFalse((Boolean) invokeMethod(vfs, "mkdir", "/a/b/c/file.txt/dir"));
        
        // 4. Opening a directory as a file should fail
        assertNull(invokeMethod(vfs, "open", "/a/b", "r"));
    }
    
    @Test
    public void testOpenFilesAreNotFreedOnUnlink() throws Exception {
        Object vfs = createVFS();
        if (vfs.getClass().getName().contains("v1_basic")) return; // Only for v2
        
        invokeMethod(vfs, "mkdir", "/dir1");
        invokeMethod(vfs, "create", "/dir1/file1");
        
        Object fd = invokeMethod(vfs, "open", "/dir1/file1", "w");
        assertNotNull(fd);
        
        Object inode = invokeMethod(vfs, "stat", "/dir1/file1");
        assertNotNull(inode);
        assertEquals(1, (int) getLinkCount(inode));
        assertEquals(1, (int) getOpenCount(inode));
        
        assertTrue((Boolean) invokeMethod(vfs, "unlink", "/dir1/file1"));
        assertEquals(0, (int) getLinkCount(inode));
        assertEquals(1, (int) getOpenCount(inode));
        
        Map<?, ?> inodes = (Map<?, ?>) invokeMethod(vfs, "getInodes");
        assertTrue(inodes.containsKey(getInodeId(inode)));
        
        invokeMethod(vfs, "close", fd);
        assertEquals(0, (int) getOpenCount(inode));
        
        Map<?, ?> inodesAfter = (Map<?, ?>) invokeMethod(vfs, "getInodes");
        assertFalse(inodesAfter.containsKey(getInodeId(inode)));
    }
}
