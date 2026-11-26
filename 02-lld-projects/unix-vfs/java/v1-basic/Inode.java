package v1_basic;

import java.util.HashMap;
import java.util.Map;

public class Inode {
    private final int inodeId;
    private final FileType fileType;
    private int permissions;
    private int linkCount;
    private byte[] data;
    private String symlinkTarget;
    private final Map<String, Integer> directoryEntries;

    public Inode(int inodeId, FileType fileType, int permissions) {
        this.inodeId = inodeId;
        this.fileType = fileType;
        this.permissions = permissions;
        this.linkCount = 1;
        this.data = new byte[0];
        this.directoryEntries = new HashMap<>();
    }

    public int getInodeId() {
        return inodeId;
    }

    public FileType getFileType() {
        return fileType;
    }

    public int getPermissions() {
        return permissions;
    }

    public void setPermissions(int permissions) {
        this.permissions = permissions;
    }

    public int getLinkCount() {
        return linkCount;
    }

    public void setLinkCount(int linkCount) {
        this.linkCount = linkCount;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }

    public String getSymlinkTarget() {
        return symlinkTarget;
    }

    public void setSymlinkTarget(String symlinkTarget) {
        this.symlinkTarget = symlinkTarget;
    }

    public Map<String, Integer> getDirectoryEntries() {
        return directoryEntries;
    }
}
