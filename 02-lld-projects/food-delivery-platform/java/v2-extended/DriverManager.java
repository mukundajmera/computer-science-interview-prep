
import java.util.ArrayList;
import java.util.List;

public class DriverManager {
    private List<Driver> drivers = new ArrayList<>();
    private DispatchStrategy dispatchStrategy;

    public DriverManager(DispatchStrategy dispatchStrategy) {
        this.dispatchStrategy = dispatchStrategy;
    }

    public void addDriver(Driver driver) {
        drivers.add(driver);
    }
    
    public List<Driver> getDrivers() {
        return drivers;
    }

    public Driver assignDriver(Restaurant restaurant) {
        while (true) {
            Driver assigned = dispatchStrategy.dispatch(restaurant, drivers);
            if (assigned == null) {
                return null;
            }
            if (assigned.tryClaim()) {
                return assigned;
            }
        }
    }
}
