/**
 * Rider.java - Ride passenger.
 */
public class Rider {
    private final String id;
    private String name;
    private String phone;

    public Rider(String id, String name, String phone) {
        this.id = id;
        this.name = name;
        this.phone = phone;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getPhone() {
        return phone;
    }

    @Override
    public String toString() {
        return String.format("Rider[%s: %s]", id, name);
    }
}
