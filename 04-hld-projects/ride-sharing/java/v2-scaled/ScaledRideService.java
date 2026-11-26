package ridesharing.v2;

import java.util.*;

public interface ScaledRideService {
    // Marker interface
}

interface AssignmentGuard {
    boolean tryAssignDriver(String rideId, String driverId, String idempotencyKey);
}

interface DriverAvailabilityStore {
    void markAvailable(String driverId);
    void markUnavailable(String driverId);
    boolean isAvailable(String driverId);
}

interface LocationIngestionService {
    void ingestLocation(String driverId, double lat, double lng, long timestampMillis);
}

class HexCell {
    public final int q;
    public final int r;

    public HexCell(int q, int r) {
        this.q = q;
        this.r = r;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        HexCell hexCell = (HexCell) o;
        return q == hexCell.q && r == hexCell.r;
    }

    @Override
    public int hashCode() {
        return Objects.hash(q, r);
    }

    @Override
    public String toString() {
        return q + "," + r;
    }
}

class H3SpatialIndexer {
    private final double resolutionStep;
    private final Map<String, Set<String>> cellToDrivers = new HashMap<>();
    private final Map<String, HexCell> driverToCell = new HashMap<>();

    public H3SpatialIndexer() {
        this(0.01);
    }

    public H3SpatialIndexer(double resolutionStep) {
        this.resolutionStep = resolutionStep;
    }

    public HexCell latLngToCell(double lat, double lng) {
        double x = lng * Math.cos(Math.toRadians(lat)) / resolutionStep;
        double y = lat / resolutionStep;

        double q = (2.0 / 3.0 * x);
        double r = (-1.0 / 3.0 * x + Math.sqrt(3.0) / 3.0 * y);

        return roundHex(q, r);
    }

    private HexCell roundHex(double q, double r) {
        double s = -q - r;
        long qRound = Math.round(q);
        long rRound = Math.round(r);
        long sRound = Math.round(s);

        double qDiff = Math.abs(qRound - q);
        double rDiff = Math.abs(rRound - r);
        double sDiff = Math.abs(sRound - s);

        if (qDiff > rDiff && qDiff > sDiff) {
            qRound = -rRound - sRound;
        } else if (rDiff > sDiff) {
            rRound = -qRound - sRound;
        }

        return new HexCell((int) qRound, (int) rRound);
    }

    public List<HexCell> getKRing(HexCell center, int k) {
        List<HexCell> results = new ArrayList<>();
        for (int dq = -k; dq <= k; dq++) {
            for (int dr = Math.max(-k, -dq - k); dr <= Math.min(k, -dq + k); dr++) {
                results.add(new HexCell(center.q + dq, center.r + dr));
            }
        }
        return results;
    }

    public synchronized void updateDriverLocation(String driverId, double lat, double lng) {
        HexCell cell = latLngToCell(lat, lng);
        HexCell oldCell = driverToCell.get(driverId);

        if (!cell.equals(oldCell)) {
            if (oldCell != null) {
                String oldCellStr = oldCell.toString();
                Set<String> oldSet = cellToDrivers.get(oldCellStr);
                if (oldSet != null) {
                    oldSet.remove(driverId);
                }
            }

            driverToCell.put(driverId, cell);
            String cellStr = cell.toString();
            cellToDrivers.computeIfAbsent(cellStr, k -> new HashSet<>()).add(driverId);
        }
    }

    public synchronized List<String> findDriversInKRing(double lat, double lng, int k) {
        HexCell center = latLngToCell(lat, lng);
        List<HexCell> cells = getKRing(center, k);
        Set<String> drivers = new HashSet<>();
        
        for (HexCell cell : cells) {
            Set<String> cellDrivers = cellToDrivers.get(cell.toString());
            if (cellDrivers != null) {
                drivers.addAll(cellDrivers);
            }
        }
        
        return new ArrayList<>(drivers);
    }
}
