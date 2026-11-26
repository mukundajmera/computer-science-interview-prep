import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class SpatialIndex {
    private final Map<String, Set<String>> grid = new ConcurrentHashMap<>();
    private final Lock lock = new ReentrantLock();

    public void addDriver(Driver driver) {
        String gh = toGeohash(driver.getLocation(), 5);
        lock.lock();
        try {
            grid.computeIfAbsent(gh, k -> ConcurrentHashMap.newKeySet()).add(driver.getDriverId());
        } finally {
            lock.unlock();
        }
    }

    public void removeDriver(Driver driver) {
        String gh = toGeohash(driver.getLocation(), 5);
        lock.lock();
        try {
            Set<String> drivers = grid.get(gh);
            if (drivers != null) {
                drivers.remove(driver.getDriverId());
                if (drivers.isEmpty()) {
                    grid.remove(gh);
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public Set<String> getDriversInGeohash(String geohash) {
        lock.lock();
        try {
            Set<String> drivers = grid.get(geohash);
            return drivers != null ? drivers : Collections.emptySet();
        } finally {
            lock.unlock();
        }
    }

    public String toGeohash(Location location, int precision) {
        long latGrid = Math.round(location.getLat() * precision);
        long lonGrid = Math.round(location.getLon() * precision);
        return latGrid + "," + lonGrid;
    }
}
