package builder.v1;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Builder Pattern - V1 Basic (Fluent Inner Class Builder)
 * 
 * Most common and recommended approach in modern Java.
 * Uses inner static class with fluent interface.
 */

// Product class - immutable
class Pizza {
    private final String size;
    private final String crust;
    private final String sauce;
    private final List<String> toppings;
    private final boolean extraCheese;
    private final boolean glutenFree;

    // Private constructor - only Builder can create
    private Pizza(Builder builder) {
        this.size = builder.size;
        this.crust = builder.crust;
        this.sauce = builder.sauce;
        this.toppings = Collections.unmodifiableList(new ArrayList<>(builder.toppings));
        this.extraCheese = builder.extraCheese;
        this.glutenFree = builder.glutenFree;
    }

    // Getters only - immutable
    public String getSize() {
        return size;
    }

    public String getCrust() {
        return crust;
    }

    public String getSauce() {
        return sauce;
    }

    public List<String> getToppings() {
        return toppings;
    }

    public boolean hasExtraCheese() {
        return extraCheese;
    }

    public boolean isGlutenFree() {
        return glutenFree;
    }

    @Override
    public String toString() {
        return String.format(
                "Pizza [%s, %s crust, %s sauce, toppings=%s, extraCheese=%s, glutenFree=%s]",
                size, crust, sauce, toppings, extraCheese, glutenFree);
    }

    // Static inner Builder class
    public static class Builder {
        // Required parameters
        private final String size;

        // Optional parameters with defaults
        private String crust = "regular";
        private String sauce = "tomato";
        private List<String> toppings = new ArrayList<>();
        private boolean extraCheese = false;
        private boolean glutenFree = false;

        // Constructor with required parameter
        public Builder(String size) {
            this.size = size;
        }

        // Fluent methods for optional parameters
        public Builder crust(String crust) {
            this.crust = crust;
            return this;
        }

        public Builder sauce(String sauce) {
            this.sauce = sauce;
            return this;
        }

        public Builder addTopping(String topping) {
            this.toppings.add(topping);
            return this;
        }

        public Builder extraCheese() {
            this.extraCheese = true;
            return this;
        }

        public Builder glutenFree() {
            this.glutenFree = true;
            return this;
        }

        // Build method - creates immutable Product
        public Pizza build() {
            // Validation
            if (size == null || size.isEmpty()) {
                throw new IllegalStateException("Size is required");
            }
            return new Pizza(this);
        }
    }
}

// Another example - Computer builder
class Computer {
    private final String cpu;
    private final int ram;
    private final int storage;
    private final String gpu;
    private final boolean bluetooth;
    private final boolean wifi;

    private Computer(Builder builder) {
        this.cpu = builder.cpu;
        this.ram = builder.ram;
        this.storage = builder.storage;
        this.gpu = builder.gpu;
        this.bluetooth = builder.bluetooth;
        this.wifi = builder.wifi;
    }

    @Override
    public String toString() {
        return String.format(
                "Computer [CPU=%s, RAM=%dGB, Storage=%dGB, GPU=%s, BT=%s, WiFi=%s]",
                cpu, ram, storage, gpu, bluetooth, wifi);
    }

    public static class Builder {
        // Required
        private final String cpu;
        private final int ram;

        // Optional with defaults
        private int storage = 256;
        private String gpu = "Integrated";
        private boolean bluetooth = true;
        private boolean wifi = true;

        public Builder(String cpu, int ram) {
            this.cpu = cpu;
            this.ram = ram;
        }

        public Builder storage(int gb) {
            this.storage = gb;
            return this;
        }

        public Builder gpu(String gpu) {
            this.gpu = gpu;
            return this;
        }

        public Builder noBluetooth() {
            this.bluetooth = false;
            return this;
        }

        public Builder noWifi() {
            this.wifi = false;
            return this;
        }

        public Computer build() {
            if (ram < 4) {
                throw new IllegalStateException("Minimum 4GB RAM required");
            }
            return new Computer(this);
        }
    }
}

// Demo
class BuilderDemo {
    public static void main(String[] args) {
        System.out.println("=== Builder Pattern Demo ===\n");

        // Build pizzas with fluent interface
        System.out.println("--- Building Pizzas ---\n");

        // Simple pizza - just size
        Pizza margherita = new Pizza.Builder("medium")
                .build();
        System.out.println("Margherita: " + margherita);

        // Customized pizza
        Pizza meat = new Pizza.Builder("large")
                .crust("thick")
                .sauce("bbq")
                .addTopping("pepperoni")
                .addTopping("sausage")
                .addTopping("bacon")
                .extraCheese()
                .build();
        System.out.println("Meat Lovers: " + meat);

        // Healthy pizza
        Pizza veggie = new Pizza.Builder("small")
                .crust("thin")
                .glutenFree()
                .addTopping("spinach")
                .addTopping("tomatoes")
                .addTopping("mushrooms")
                .build();
        System.out.println("Veggie: " + veggie);

        System.out.println("\n--- Building Computers ---\n");

        // Basic computer
        Computer basic = new Computer.Builder("Intel i5", 8)
                .build();
        System.out.println("Basic: " + basic);

        // Gaming computer
        Computer gaming = new Computer.Builder("Intel i9", 32)
                .storage(2000)
                .gpu("RTX 4090")
                .build();
        System.out.println("Gaming: " + gaming);

        // Server (no bluetooth/wifi needed)
        Computer server = new Computer.Builder("AMD EPYC", 128)
                .storage(8000)
                .noBluetooth()
                .noWifi()
                .build();
        System.out.println("Server: " + server);
    }
}
