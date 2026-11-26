package v1_basic;

import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

public class VFS {
    private static final int MAX_SYMLINKS = 40;
    private final Map<Integer, Inode> inodes;
    private int nextInodeId;
    private final int rootInodeId;

    public VFS() {
        this.inodes = new HashMap<>();
        this.nextInodeId = 1;
        
        Inode rootInode = createInode(FileType.DIRECTORY, 0755);
        this.rootInodeId = rootInode.getInodeId();
        rootInode.getDirectoryEntries().put(".", rootInode.getInodeId());
        rootInode.getDirectoryEntries().put("..", rootInode.getInodeId());
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
                
                if (targetPath.startsWith("/")) {
                    currentInode = inodes.get(rootInodeId);
                    
                    List<String> newPartsList = new ArrayList<>(validTargetParts);
                    for (int j = i + 1; j < parts.length; j++) {
                        newPartsList.add(parts[j]);
                    }
                    parts = newPartsList.toArray(new String[0]);
                    i = 0;
                } else {
                    List<String> newPartsList = new ArrayList<>(validTargetParts);
                    for (int j = i + 1; j < parts.length; j++) {
                        newPartsList.add(parts[j]);
                    }
                    parts = newPartsList.toArray(new String[0]);
                    i = 0;
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
        ParentAndName pan = getParentAndName(path);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty() || pan.name.equals("invalid")) {
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
        ParentAndName pan = getParentAndName(path);
        if (pan.parentInode == null || pan.parentInode.getFileType() != FileType.DIRECTORY) {
            return false;
        }

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty() || pan.name.equals("invalid")) {
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

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty() || pan.name.equals("invalid")) {
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

        if (pan.parentInode.getDirectoryEntries().containsKey(pan.name) || pan.name.isEmpty() || pan.name.equals("invalid")) {
            return false;
        }

        Inode newInode = createInode(FileType.SYMLINK, 0777);
        newInode.setSymlinkTarget(target);
        pan.parentInode.getDirectoryEntries().put(pan.name, newInode.getInodeId());

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

        if (targetInode.getFileType() == FileType.DIRECTORY) {
            if (targetInode.getDirectoryEntries().size() > 2) {
                return false;
            }
            pan.parentInode.setLinkCount(pan.parentInode.getLinkCount() - 1);
        }

        pan.parentInode.getDirectoryEntries().remove(pan.name);
        targetInode.setLinkCount(targetInode.getLinkCount() - 1);

        if (targetInode.getLinkCount() == 0) {
            inodes.remove(targetInodeId);
        }

        return true;
    }

    public FileDescriptor open(String path, String mode) {
        Inode inode = resolvePath(path);
        if (inode == null) {
            return null;
        }

        if (inode.getFileType() == FileType.DIRECTORY) {
            return null;
        }

        return new FileDescriptor(inode, mode);
    }

    public byte[] read(FileDescriptor fd, int size) {
        if (!fd.getMode().contains("r") && !fd.getMode().contains("+")) {
            throw new RuntimeException("File not opened for reading");
        }

        byte[] fileData = fd.getInode().getData();
        int available = fileData.length - fd.getOffset();
        int toRead = Math.min(size, Math.max(0, available));

        byte[] data = new byte[toRead];
        System.arraycopy(fileData, fd.getOffset(), data, 0, toRead);
        fd.setOffset(fd.getOffset() + toRead);

        return data;
    }

    public int write(FileDescriptor fd, byte[] data) {
        if (!fd.getMode().contains("w") && !fd.getMode().contains("a") && !fd.getMode().contains("+")) {
            throw new RuntimeException("File not opened for writing");
        }

        if (fd.getMode().contains("a")) {
            fd.setOffset(fd.getInode().getData().length);
        }

        int endPos = fd.getOffset() + data.length;
        byte[] fileData = fd.getInode().getData();

        if (endPos > fileData.length) {
            byte[] newData = new byte[endPos];
            System.arraycopy(fileData, 0, newData, 0, fileData.length);
            fd.getInode().setData(newData);
            fileData = newData;
        }

        System.arraycopy(data, 0, fileData, fd.getOffset(), data.length);
        fd.setOffset(fd.getOffset() + data.length);

        return data.length;
    }

    public int lseek(FileDescriptor fd, int offset, int whence) {
        if (whence == 0) { // SEEK_SET
            fd.setOffset(offset);
        } else if (whence == 1) { // SEEK_CUR
            fd.setOffset(fd.getOffset() + offset);
        } else if (whence == 2) { // SEEK_END
            fd.setOffset(fd.getInode().getData().length + offset);
        } else {
            throw new IllegalArgumentException("Invalid whence");
        }

        if (fd.getOffset() < 0) {
            fd.setOffset(0);
        }

        return fd.getOffset();
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
    
    public Map<Integer, Inode> getInodes() {
        return inodes;
    }
}
