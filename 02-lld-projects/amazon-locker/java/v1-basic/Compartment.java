public class Compartment {
    private final String id;
    private final PackageSize size;
    private boolean occupied;

    public Compartment(String id, PackageSize size) {
        this.id = id;
        this.size = size;
        this.occupied = false;
    }

    public String getId() {
        return id;
    }

    public PackageSize getSize() {
        return size;
    }

    public boolean isAvailable() {
        return !occupied;
    }

    public void markOccupied() {
        this.occupied = true;
    }

    public void markAvailable() {
        this.occupied = false;
    }
}
