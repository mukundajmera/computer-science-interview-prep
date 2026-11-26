package v1_basic;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Trip {
    private final String tripId;
    private final Rider rider;
    private Driver driver;
    private final Location origin;
    private final Location destination;
    private final double price;
    private TripState state;
    private final Lock lock = new ReentrantLock();

    public Trip(String tripId, Rider rider, Location origin, Location destination, double price) {
        this.tripId = tripId;
        this.rider = rider;
        this.origin = origin;
        this.destination = destination;
        this.price = price;
        this.state = TripState.REQUESTED;
    }

    public String getTripId() {
        return tripId;
    }

    public Rider getRider() {
        return rider;
    }

    public Driver getDriver() {
        lock.lock();
        try {
            return driver;
        } finally {
            lock.unlock();
        }
    }

    public TripState getState() {
        lock.lock();
        try {
            return state;
        } finally {
            lock.unlock();
        }
    }

    public void setState(TripState state) {
        lock.lock();
        try {
            this.state = state;
        } finally {
            lock.unlock();
        }
    }

    public boolean assignDriver(Driver driver) {
        lock.lock();
        try {
            if (this.state == TripState.REQUESTED) {
                this.driver = driver;
                this.state = TripState.ACCEPTED;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }
}
