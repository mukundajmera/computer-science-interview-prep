package ridesharing.v1;

import java.util.List;
import java.util.Optional;

public interface RideService {
    Ride requestRide(RequestRideCommand command, String idempotencyKey);
    Ride acceptRide(String rideId, String driverId, String idempotencyKey);
    Ride updateRideState(String rideId, RideState nextState);
    Optional<Ride> getRide(String rideId);
}

interface LocationIndex {
    List<DriverCandidate> findNearby(double lat, double lng, double radiusKm, int limit);
}

enum RideState {
    REQUESTED,
    MATCH_PENDING,
    MATCHED,
    DRIVER_EN_ROUTE,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
}

final class RequestRideCommand {
    public final String riderId;
    public final double pickupLat;
    public final double pickupLng;
    public final double dropoffLat;
    public final double dropoffLng;

    RequestRideCommand(String riderId, double pickupLat, double pickupLng,
                       double dropoffLat, double dropoffLng) {
        this.riderId = riderId;
        this.pickupLat = pickupLat;
        this.pickupLng = pickupLng;
        this.dropoffLat = dropoffLat;
        this.dropoffLng = dropoffLng;
    }
}

final class Ride {
    public final String rideId;
    public final String riderId;
    public final String driverId;
    public final RideState state;

    Ride(String rideId, String riderId, String driverId, RideState state) {
        this.rideId = rideId;
        this.riderId = riderId;
        this.driverId = driverId;
        this.state = state;
    }
}

final class DriverCandidate {
    public final String driverId;
    public final double etaMinutes;

    DriverCandidate(String driverId, double etaMinutes) {
        this.driverId = driverId;
        this.etaMinutes = etaMinutes;
    }
}
