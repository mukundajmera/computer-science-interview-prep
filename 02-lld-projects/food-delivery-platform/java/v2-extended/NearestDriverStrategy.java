
import java.util.List;

public class NearestDriverStrategy implements DispatchStrategy {
    @Override
    public Driver dispatch(Restaurant restaurant, List<Driver> drivers) {
        Driver nearest = null;
        double minDistance = Double.MAX_VALUE;
        
        for (Driver driver : drivers) {
            if (driver.isAvailable()) {
                double distance = driver.getLocation().distanceTo(restaurant.getLocation());
                if (distance < minDistance) {
                    minDistance = distance;
                    nearest = driver;
                }
            }
        }
        return nearest;
    }
}
