package models;

/**
 * Customer.java - Rental customer entity.
 */
public class Customer {
    private final String id;
    private String name;
    private String email;
    private String driversLicense;

    public Customer(String id, String name, String email, String driversLicense) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.driversLicense = driversLicense;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public String getDriversLicense() {
        return driversLicense;
    }

    @Override
    public String toString() {
        return String.format("Customer[%s: %s]", id, name);
    }
}
