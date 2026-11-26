package v1_basic;

public class FileDescriptor {
    private final Inode inode;
    private final String mode;
    private int offset;

    public FileDescriptor(Inode inode, String mode) {
        this.inode = inode;
        this.mode = mode;
        this.offset = 0;
    }

    public Inode getInode() {
        return inode;
    }

    public String getMode() {
        return mode;
    }

    public int getOffset() {
        return offset;
    }

    public void setOffset(int offset) {
        this.offset = offset;
    }
}
