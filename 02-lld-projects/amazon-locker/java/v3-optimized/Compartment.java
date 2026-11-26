public class Compartment {
    private final String id;
    private final PackageSize size;
    private CompartmentStatus status;

    public Compartment(String id, PackageSize size) {
        this.id = id;
        this.size = size;
        this.status = CompartmentStatus.AVAILABLE;
    }

    public String getId() {
        return id;
    }

    public PackageSize getSize() {
        return size;
    }

    public CompartmentStatus getStatus() {
        return status;
    }

    public boolean isAvailable() {
        return status == CompartmentStatus.AVAILABLE;
    }

    public void markOccupied() {
        this.status = CompartmentStatus.OCCUPIED;
    }

    public void markAvailable() {
        this.status = CompartmentStatus.AVAILABLE;
    }

    public void markOutOfService() {
        this.status = CompartmentStatus.OUT_OF_SERVICE;
    }

    public void markInService() {
        if (this.status == CompartmentStatus.OUT_OF_SERVICE) {
            this.status = CompartmentStatus.AVAILABLE;
        }
    }
}
