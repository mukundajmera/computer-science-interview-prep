package v2_extended;

import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;

public class UnixVfs {
    public enum FileType { FILE, DIRECTORY, SYMLINK }
    
    public static class Inode {
        private final int inodeId;
        private final FileType fileType;
        private int permissions;
        private int linkCount;
        private int openCount;
        private byte[] data;
        private String symlinkTarget;
        private final Map<String, Integer> directoryEntries;

        public Inode(int inodeId, FileType fileType, int permissions) {
            this.inodeId = inodeId;
            this.fileType = fileType;
            this.permissions = permissions;
            this.linkCount = 1;
            this.openCount = 0;
            this.data = new byte[0];
            this.directoryEntries = new HashMap<>();
        }

        public int getInodeId() { return inodeId; }
        public FileType getFileType() { return fileType; }
        public int getPermissions() { return permissions; }
        public void setPermissions(int permissions) { this.permissions = permissions; }
        public int getLinkCount() { return linkCount; }
        public void setLinkCount(int linkCount) { this.linkCount = linkCount; }
        public int getOpenCount() { return openCount; }
        public void setOpenCount(int openCount) { this.openCount = openCount; }
        public byte[] getData() { return data; }
        public void setData(byte[] data) { this.data = data; }
        public String getSymlinkTarget() { return symlinkTarget; }
        public void setSymlinkTarget(String target) { this.symlinkTarget = target; }
        public Map<String, Integer> getDirectoryEntries() { return directoryEntries; }
    }

    public static class FileDescriptor {
        private final Inode inode;
        private final String mode;
        private int offset;
        private boolean closed;

        public FileDescriptor(Inode inode, String mode) {
            this.inode = inode;
            this.mode = mode;
            this.offset = 0;
            this.closed = false;
        }

        public Inode getInode() { return inode; }
        public String getMode() { return mode; }
        public int getOffset() { return offset; }
        public void setOffset(int offset) { this.offset = offset; }
        public boolean isClosed() { return closed; }
        public void setClosed(boolean closed) { this.closed = closed; }
    }

    private static final int MAX_SYMLINKS = 40;
    private final Map<Integer, Inode> inodes;
    private int nextInodeId;
    private final int rootInodeId;

    public UnixVfs() {
        this.inodes = new HashMap<>();
        this.nextInodeId = 1;
        
        Inode rootInode = createInode(FileType.DIRECTORY, 0755);
        this.rootInodeId = rootInode.getInodeId();
        rootInode.getDirectoryEntries().put(".", rootInode.getInodeId());
        rootInode.getDirectoryEntries().put("..", rootInode.getInodeId());
    }

    public Map<Integer, Inode> getInodes() {
        return inodes;
    }

    private Inode createInode(FileType fileType, int permissions) {
        Inode inode = new Inode(nextInodeId, fileType, permissions);
        inodes.put(nextInodeId, inode);
        nextInodeId++;
        return inode;
    }

    public Inode resolvePath(String path) {
        return resolvePath(path, true);
    }

    private Inode resolvePath(String path, boolean followSymlink) {
        if (path == null || !path.startsWith("/")) {
            return null; // Only absolute paths supported
        }

        Inode currentInode = inodes.get(rootInodeId);
        String[] pathParts = path.split("/");
        List<String> partsList = new ArrayList<>();
        for (String p : pathParts) {
            if (p != null && !p.isEmpty()) {
                partsList.add(p);
            }
        }
        
        String[] parts = partsList.toArray(new String[0]);
        
        int symlinkCount = 0;
        int i = 0;
        
        while (i < parts.length) {
            String part = parts[i];

            if (!currentInode.getDirectoryEntries().containsKey(part)) {
                return null;
            }

            int nextInodeId = currentInode.getDirectoryEntries().get(part);
            Inode nextInode = inodes.get(nextInodeId);

            if (i == parts.length - 1 && !followSymlink) {
                return nextInode;
            }

            if (nextInode.getFileType() == FileType.SYMLINK) {
                symlinkCount++;
                if (symlinkCount > MAX_SYMLINKS) {
                    throw new RuntimeException("Too many levels of symbolic links");
                }

                String targetPath = nextInode.getSymlinkTarget();
                if (targetPath == null) {
                    return null;
                }

                String[] targetParts = targetPath.split("/");
                List<String> validTargetParts = new ArrayList<>();
                for(String p: targetParts) {
                    if (p != null && !p.isEmpty()) {
                        validTargetParts.add(p);
                    }
                }
                
                List<String> newPartsList = new ArrayList<>(validTargetParts);
                for (int j = i + 1; j < parts.length; j++) {
                    newPartsList.add(parts[j]);
                }
                parts = newPartsList.toArray(new String[0]);
                i = 0;
                
                if (targetPath.startsWith("/")) {
                    currentInode = inodes.get(rootInodeId);
                }
            } else {
                currentInode = nextInode;
                i++;
            }
        }

        return currentInode;
    }

    private static class ParentAndName {
        Inode parentInode;
        String name;

        ParentAndName(Inode parentInode, String name) {
            this.parentInode = parentInode;
            this.name = name;
        }
    }

    private ParentAndName getParentAndName(String path) {
        if (path == null) return new ParentAndName(null, "");
        String[] parts = path.split("/");
        String name = "";
        StringBuilder parentPath = new StringBuilder();

        for (int i = 0; i < parts.length; i++) {
            if (parts[i] == null || parts[i].isEmpty()) continue;
            if (i == parts.length - 1) {
                name = parts[i];
            } else {
                parentPath.append("/").append(parts[i]);
            }
        }

        if (parentPath.length() == 0) {
            parentPath.append("/");
        }

        Inode parentInode = resolvePath(parentPath.toString());
        return new ParentAndName(parentInode, name);
    }

    public boolean mkdir(String path) {
        return mkdir(path, 0755);
    }

    public boolean mkdir(String path, int permissions) {
        if (path == null || path.trim().isEmpty() || !path.startsWith("/")) return false;
        ParentAndName pan = getParentAndName(path);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty()) {
            return false;
        }

        Inode newInode = createInode(FileType.DIRECTORY, permissions);
        newInode.getDirectoryEntries().put(".", newInode.getInodeId());
        newInode.getDirectoryEntries().put("..", pan.parentInode.getInodeId());

        pan.parentInode.getDirectoryEntries().put(pan.name, newInode.getInodeId());
        pan.parentInode.setLinkCount(pan.parentInode.getLinkCount() + 1);

        return true;
    }

    public boolean create(String path) {
        return create(path, 0644);
    }

    public boolean create(String path, int permissions) {
        if (path == null || path.trim().isEmpty() || !path.startsWith("/")) return false;
        ParentAndName pan = getParentAndName(path);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty()) {
            return false;
        }

        Inode newInode = createInode(FileType.FILE, permissions);
        pan.parentInode.getDirectoryEntries().put(pan.name, newInode.getInodeId());

        return true;
    }

    public boolean link(String oldPath, String newPath) {
        Inode targetInode = resolvePath(oldPath);
        if (targetInode == null || targetInode.getFileType() == FileType.DIRECTORY) {
            return false;
        }

        ParentAndName pan = getParentAndName(newPath);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty()) {
            return false;
        }

        pan.parentInode.getDirectoryEntries().put(pan.name, targetInode.getInodeId());
        targetInode.setLinkCount(targetInode.getLinkCount() + 1);

        return true;
    }

    public boolean symlink(String target, String linkPath) {
        ParentAndName pan = getParentAndName(linkPath);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty()) {
            return false;
        }

        Inode symlinkInode = createInode(FileType.SYMLINK, 0777);
        symlinkInode.setSymlinkTarget(target);

        pan.parentInode.getDirectoryEntries().put(pan.name, symlinkInode.getInodeId());

        return true;
    }

    public boolean unlink(String path) {
        ParentAndName pan = getParentAndName(path);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (!pan.parentInode.getDirectoryEntries().containsKey(pan.name)) {
            return false;
        }

        int targetInodeId = pan.parentInode.getDirectoryEntries().get(pan.name);
        Inode targetInode = inodes.get(targetInodeId);
        if (targetInode == null) {
            return false;
        }
        
        if (targetInode.getFileType() == FileType.DIRECTORY) {
            if (targetInode.getDirectoryEntries().size() > 2) { // more than . and ..
                return false;
            }
        }

        pan.parentInode.getDirectoryEntries().remove(pan.name);
        
        // Remove link to parent directory if it's a directory
        if (targetInode.getFileType() == FileType.DIRECTORY) {
            pan.parentInode.setLinkCount(pan.parentInode.getLinkCount() - 1);
        }

        targetInode.setLinkCount(targetInode.getLinkCount() - 1);
        
        checkAndFreeInode(targetInode);

        return true;
    }
    
    private void checkAndFreeInode(Inode inode) {
        if (inode.getLinkCount() <= 0 && inode.getOpenCount() <= 0) {
            inodes.remove(inode.getInodeId());
        }
    }

    public FileDescriptor open(String path, String mode) {
        Inode inode = resolvePath(path);
        if (inode == null || inode.getFileType() == FileType.DIRECTORY) {
            return null;
        }
        inode.setOpenCount(inode.getOpenCount() + 1);
        return new FileDescriptor(inode, mode);
    }
    
    public void close(FileDescriptor fd) {
        if (fd == null || fd.isClosed()) return;
        fd.setClosed(true);
        Inode inode = fd.getInode();
        inode.setOpenCount(inode.getOpenCount() - 1);
        checkAndFreeInode(inode);
    }

    public byte[] read(FileDescriptor fd, int size) {
        if (fd == null || fd.isClosed() || (!fd.getMode().contains("r") && !fd.getMode().contains("+"))) {
            return null;
        }

        Inode inode = fd.getInode();
        byte[] data = inode.getData();
        int offset = fd.getOffset();

        if (offset >= data.length) {
            return new byte[0];
        }

        int bytesToRead = Math.min(size, data.length - offset);
        byte[] result = Arrays.copyOfRange(data, offset, offset + bytesToRead);
        fd.setOffset(offset + bytesToRead);
        
        return result;
    }

    public int write(FileDescriptor fd, byte[] writeData) {
        if (fd == null || fd.isClosed() || (!fd.getMode().contains("w") && !fd.getMode().contains("+") && !fd.getMode().contains("a"))) {
            return -1;
        }

        Inode inode = fd.getInode();
        byte[] data = inode.getData();
        int offset = fd.getOffset();

        if (fd.getMode().contains("a")) {
            offset = data.length;
            fd.setOffset(offset);
        }

        int newLength = Math.max(data.length, offset + writeData.length);
        byte[] newData = new byte[newLength];
        
        System.arraycopy(data, 0, newData, 0, data.length);
        System.arraycopy(writeData, 0, newData, offset, writeData.length);
        
        inode.setData(newData);
        fd.setOffset(offset + writeData.length);

        return writeData.length;
    }

    public int lseek(FileDescriptor fd, int offset, int whence) {
        if (fd == null || fd.isClosed()) return -1;
        
        Inode inode = fd.getInode();
        int newOffset = -1;

        switch (whence) {
            case 0: // SEEK_SET
                newOffset = offset;
                break;
            case 1: // SEEK_CUR
                newOffset = fd.getOffset() + offset;
                break;
            case 2: // SEEK_END
                newOffset = inode.getData().length + offset;
                break;
        }

        if (newOffset < 0) {
            return -1; // Invalid offset
        }

        fd.setOffset(newOffset);
        return newOffset;
    }

    public boolean chmod(String path, int mode) {
        Inode inode = resolvePath(path);
        if (inode == null) {
            return false;
        }
        inode.setPermissions(mode);
        return true;
    }

    public Inode stat(String path) {
        return resolvePath(path);
    }
}
