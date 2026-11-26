
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Driver {
    private final String driverId;
    private Location location;
    private DriverState state;
    private final Lock lock = new ReentrantLock();

    public Driver(String driverId, Location location) {
        this.driverId = driverId;
        this.location = location;
        this.state = DriverState.OFFLINE;
    }

    public String getDriverId() {
        return driverId;
    }

    public Location getLocation() {
        lock.lock();
        try {
            return location;
        } finally {
            lock.unlock();
        }
    }

    public void updateLocation(Location location) {
        lock.lock();
        try {
            if (location.getTimestamp() >= this.location.getTimestamp()) {
                this.location = location;
            }
        } finally {
            lock.unlock();
        }
    }

    public DriverState getState() {
        lock.lock();
        try {
            return state;
        } finally {
            lock.unlock();
        }
    }

    public boolean transitionState(DriverState newState) {
        lock.lock();
        try {
            boolean valid = false;
            if (state == DriverState.OFFLINE && newState == DriverState.IDLE) {
                valid = true;
            } else if (state == DriverState.IDLE && newState == DriverState.ASSIGNED) {
                valid = true;
            } else if (state == DriverState.IDLE && newState == DriverState.OFFLINE) {
                valid = true;
            } else if (state == DriverState.ASSIGNED && newState == DriverState.IN_TRIP) {
                valid = true;
            } else if (state == DriverState.ASSIGNED && newState == DriverState.IDLE) {
                valid = true;
            } else if (state == DriverState.IN_TRIP && newState == DriverState.IDLE) {
                valid = true;
            } else if (state == DriverState.IN_TRIP && newState == DriverState.OFFLINE) {
                valid = true;
            }

            if (valid) {
                this.state = newState;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }
}
