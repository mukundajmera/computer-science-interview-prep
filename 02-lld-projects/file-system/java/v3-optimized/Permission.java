/**
 * File System - V3 Optimized
 * 
 * Permission class for access control (Unix-style).
 */
class Permission {
    private boolean read;
    private boolean write;
    private boolean execute;

    public Permission() {
        // Default: read and write, no execute
        this.read = true;
        this.write = true;
        this.execute = false;
    }

    public Permission(boolean read, boolean write, boolean execute) {
        this.read = read;
        this.write = write;
        this.execute = execute;
    }

    /**
     * Create permission from Unix-style octal (e.g., 7 = rwx, 6 = rw-, 4 = r--)
     */
    public static Permission fromOctal(int octal) {
        if (octal < 0 || octal > 7) {
            throw new IllegalArgumentException("Octal must be 0-7");
        }
        boolean read = (octal & 4) != 0;
        boolean write = (octal & 2) != 0;
        boolean execute = (octal & 1) != 0;
        return new Permission(read, write, execute);
    }

    public boolean canRead() {
        return read;
    }

    public boolean canWrite() {
        return write;
    }

    public boolean canExecute() {
        return execute;
    }

    public void setRead(boolean read) {
        this.read = read;
    }

    public void setWrite(boolean write) {
        this.write = write;
    }

    public void setExecute(boolean execute) {
        this.execute = execute;
    }

    public void setAll(boolean read, boolean write, boolean execute) {
        this.read = read;
        this.write = write;
        this.execute = execute;
    }

    /**
     * Convert to Unix-style octal.
     */
    public int toOctal() {
        int octal = 0;
        if (read) octal += 4;
        if (write) octal += 2;
        if (execute) octal += 1;
        return octal;
    }

    /**
     * Copy this permission.
     */
    public Permission copy() {
        return new Permission(read, write, execute);
    }

    @Override
    public String toString() {
        return (read ? "r" : "-") + (write ? "w" : "-") + (execute ? "x" : "-");
    }
}

/**
 * Full permission set (owner/group/others).
 */
class PermissionSet {
    private Permission owner;
    private Permission group;
    private Permission others;

    public PermissionSet() {
        // Default: owner=rwx, group=rx, others=rx (755)
        this.owner = new Permission(true, true, true);
        this.group = new Permission(true, false, true);
        this.others = new Permission(true, false, true);
    }

    public PermissionSet(int ownerOctal, int groupOctal, int othersOctal) {
        this.owner = Permission.fromOctal(ownerOctal);
        this.group = Permission.fromOctal(groupOctal);
        this.others = Permission.fromOctal(othersOctal);
    }

    public Permission getOwner() {
        return owner;
    }

    public Permission getGroup() {
        return group;
    }

    public Permission getOthers() {
        return others;
    }

    public void setOwner(Permission owner) {
        this.owner = owner;
    }

    public void setGroup(Permission group) {
        this.group = group;
    }

    public void setOthers(Permission others) {
        this.others = others;
    }

    /**
     * Set from Unix-style mode (e.g., 755, 644).
     */
    public void setMode(int mode) {
        int ownerOctal = (mode / 100) % 10;
        int groupOctal = (mode / 10) % 10;
        int othersOctal = mode % 10;
        this.owner = Permission.fromOctal(ownerOctal);
        this.group = Permission.fromOctal(groupOctal);
        this.others = Permission.fromOctal(othersOctal);
    }

    public PermissionSet copy() {
        PermissionSet copy = new PermissionSet();
        copy.owner = owner.copy();
        copy.group = group.copy();
        copy.others = others.copy();
        return copy;
    }

    @Override
    public String toString() {
        return owner.toString() + group.toString() + others.toString();
    }
}
