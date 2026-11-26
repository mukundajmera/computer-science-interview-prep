
import java.util.concurrent.atomic.AtomicBoolean;

public class Driver {
    private String id;
    private Location location;
    private AtomicBoolean available;

    public Driver(String id, Location location) {
        this.id = id;
        this.location = location;
        this.available = new AtomicBoolean(true);
    }

    public String getId() { return id; }
    public Location getLocation() { return location; }
    public boolean isAvailable() { return available.get(); }
    
    public void setLocation(Location location) { this.location = location; }
    public void setAvailable(boolean available) { this.available.set(available); }
    
    public boolean tryClaim() {
        return this.available.compareAndSet(true, false);
    }
    
    public void release() {
        this.available.set(true);
    }
}
