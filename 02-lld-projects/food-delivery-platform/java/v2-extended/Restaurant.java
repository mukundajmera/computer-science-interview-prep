
public class Restaurant {
    private String id;
    private Location location;

    public Restaurant(String id, Location location) {
        this.id = id;
        this.location = location;
    }

    public String getId() { return id; }
    public Location getLocation() { return location; }
}
