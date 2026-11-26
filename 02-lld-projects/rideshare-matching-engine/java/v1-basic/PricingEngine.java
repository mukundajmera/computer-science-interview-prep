package v1_basic;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class PricingEngine {
    private final double baseFare;
    private final double perMileRate;
    private int activeRequests = 0;
    private int availableDrivers = 0;
    private final Lock lock = new ReentrantLock();

    public PricingEngine() {
        this(5.0, 2.0);
    }

    public PricingEngine(double baseFare, double perMileRate) {
        this.baseFare = baseFare;
        this.perMileRate = perMileRate;
    }

    public void updateSupplyDemand(int supplyDelta, int demandDelta) {
        lock.lock();
        try {
            this.availableDrivers += supplyDelta;
            this.activeRequests += demandDelta;
        } finally {
            lock.unlock();
        }
    }

    public double calculateSurgeMultiplier() {
        lock.lock();
        try {
            if (this.availableDrivers == 0) {
                return this.activeRequests > 0 ? 2.0 : 1.0;
            }

            double ratio = (double) this.activeRequests / this.availableDrivers;
            if (ratio > 2.0) {
                return 2.0;
            } else if (ratio > 1.0) {
                return 1.5;
            }
            return 1.0;
        } finally {
            lock.unlock();
        }
    }

    public double estimatePrice(Location origin, Location destination) {
        double distance = origin.distanceTo(destination);
        double surge = calculateSurgeMultiplier();
        double price = (this.baseFare + distance * this.perMileRate) * surge;
        return Math.round(price * 100.0) / 100.0;
    }
}
