/**
 * Factory Method Pattern - V2 Variant (Parameterized Factory)
 * 
 * Common variation where a single factory method accepts a parameter
 * to determine which product to create.
 */

// Product interface
interface Vehicle {
    void start();

    void stop();

    int getWheels();

    String getType();
}

// Concrete Products
class Car implements Vehicle {
    private String model;

    public Car(String model) {
        this.model = model;
    }

    @Override
    public void start() {
        System.out.println(model + " car engine started");
    }

    @Override
    public void stop() {
        System.out.println(model + " car engine stopped");
    }

    @Override
    public int getWheels() {
        return 4;
    }

    @Override
    public String getType() {
        return "Car: " + model;
    }
}

class Motorcycle implements Vehicle {
    private String brand;

    public Motorcycle(String brand) {
        this.brand = brand;
    }

    @Override
    public void start() {
        System.out.println(brand + " motorcycle revving up!");
    }

    @Override
    public void stop() {
        System.out.println(brand + " motorcycle stopped");
    }

    @Override
    public int getWheels() {
        return 2;
    }

    @Override
    public String getType() {
        return "Motorcycle: " + brand;
    }
}

class Truck implements Vehicle {
    private int capacity;

    public Truck(int capacityTons) {
        this.capacity = capacityTons;
    }

    @Override
    public void start() {
        System.out.println(capacity + "-ton truck starting...");
    }

    @Override
    public void stop() {
        System.out.println("Truck stopped");
    }

    @Override
    public int getWheels() {
        return capacity > 10 ? 18 : 6;
    }

    @Override
    public String getType() {
        return "Truck: " + capacity + " tons";
    }
}

// Vehicle types enum
enum VehicleType {
    CAR, MOTORCYCLE, TRUCK
}

// Parameterized Factory
class VehicleFactory {

    // Parameterized factory method
    public Vehicle createVehicle(VehicleType type, String config) {
        switch (type) {
            case CAR:
                return new Car(config);
            case MOTORCYCLE:
                return new Motorcycle(config);
            case TRUCK:
                return new Truck(Integer.parseInt(config));
            default:
                throw new IllegalArgumentException("Unknown vehicle type: " + type);
        }
    }

    // Convenience methods
    public Vehicle createCar(String model) {
        return createVehicle(VehicleType.CAR, model);
    }

    public Vehicle createMotorcycle(String brand) {
        return createVehicle(VehicleType.MOTORCYCLE, brand);
    }

    public Vehicle createTruck(int capacityTons) {
        return createVehicle(VehicleType.TRUCK, String.valueOf(capacityTons));
    }
}

// Demo
class ParameterizedFactoryDemo {
    public static void main(String[] args) {
        System.out.println("=== Parameterized Factory Demo ===\n");

        VehicleFactory factory = new VehicleFactory();

        // Create vehicles using parameterized factory method
        Vehicle car = factory.createVehicle(VehicleType.CAR, "Tesla Model S");
        Vehicle bike = factory.createVehicle(VehicleType.MOTORCYCLE, "Harley Davidson");
        Vehicle truck = factory.createVehicle(VehicleType.TRUCK, "20");

        // Use vehicles
        System.out.println("--- Testing Vehicles ---");

        for (Vehicle vehicle : new Vehicle[] { car, bike, truck }) {
            System.out.println("\nVehicle: " + vehicle.getType());
            System.out.println("Wheels: " + vehicle.getWheels());
            vehicle.start();
            vehicle.stop();
        }

        System.out.println("\n--- Using Convenience Methods ---");

        Vehicle sedan = factory.createCar("Honda Accord");
        Vehicle sportbike = factory.createMotorcycle("Ducati");
        Vehicle heavyTruck = factory.createTruck(30);

        System.out.println(sedan.getType() + " has " + sedan.getWheels() + " wheels");
        System.out.println(sportbike.getType() + " has " + sportbike.getWheels() + " wheels");
        System.out.println(heavyTruck.getType() + " has " + heavyTruck.getWheels() + " wheels");
    }
}
