/**
 * Driver.java - Ride driver.
 */
public class Driver {
    private final String id;
    private String name;
    private String vehicleNumber;
    private Location currentLocation;
    private boolean isAvailable;

    public Driver(String id, String name, String vehicleNumber) {
        this.id = id;
        this.name = name;
        this.vehicleNumber = vehicleNumber;
        this.isAvailable = true;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getVehicleNumber() {
        return vehicleNumber;
    }

    public Location getCurrentLocation() {
        return currentLocation;
    }

    public void setCurrentLocation(Location loc) {
        this.currentLocation = loc;
    }

    public boolean isAvailable() {
        return isAvailable;
    }

    public void setAvailable(boolean a) {
        this.isAvailable = a;
    }

    @Override
    public String toString() {
        return String.format("Driver[%s: %s]", id, name);
    }
}
