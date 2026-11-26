package ridesharing.v1;

import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;

public class RideServiceTest {

    private static class InMemoryRideService implements RideService {
        private final Map<String, Ride> rides = new HashMap<>();

        @Override
        public Ride requestRide(RequestRideCommand command, String idempotencyKey) {
            String rideId = "ride_" + idempotencyKey;
            if (rides.containsKey(rideId)) {
                return rides.get(rideId);
            }
            
            Ride ride = new Ride(
                rideId,
                command.riderId,
                null,
                RideState.REQUESTED
            );
            rides.put(rideId, ride);
            return ride;
        }

        @Override
        public Ride acceptRide(String rideId, String driverId, String idempotencyKey) {
            Ride ride = rides.get(rideId);
            if (ride == null) {
                throw new IllegalArgumentException("Ride not found");
            }
            if (ride.state != RideState.REQUESTED && ride.state != RideState.MATCH_PENDING) {
                throw new IllegalStateException("Ride cannot be accepted in its current state");
            }
            
            Ride updatedRide = new Ride(
                ride.rideId,
                ride.riderId,
                driverId,
                RideState.MATCHED
            );
            rides.put(rideId, updatedRide);
            return updatedRide;
        }

        @Override
        public Ride updateRideState(String rideId, RideState nextState) {
            Ride ride = rides.get(rideId);
            if (ride == null) {
                throw new IllegalArgumentException("Ride not found");
            }
            
            Ride updatedRide = new Ride(
                ride.rideId,
                ride.riderId,
                ride.driverId,
                nextState
            );
            rides.put(rideId, updatedRide);
            return updatedRide;
        }

        @Override
        public Optional<Ride> getRide(String rideId) {
            return Optional.ofNullable(rides.get(rideId));
        }
    }

    @Test
    void testRequestRideCreatesNewRide() {
        RideService service = new InMemoryRideService();
        RequestRideCommand command = new RequestRideCommand(
            "rider_123",
            37.7749,
            -122.4194,
            37.3382,
            -121.8863
        );

        Ride ride = service.requestRide(command, "idemp_abc");

        assertEquals("ride_idemp_abc", ride.rideId);
        assertEquals("rider_123", ride.riderId);
        assertNull(ride.driverId);
        assertEquals(RideState.REQUESTED, ride.state);

        // Verify idempotency
        Ride rideAgain = service.requestRide(command, "idemp_abc");
        assertSame(ride, rideAgain);
    }

    @Test
    void testAcceptRideUpdatesDriverAndState() {
        RideService service = new InMemoryRideService();
        RequestRideCommand command = new RequestRideCommand(
            "rider_123",
            37.7749,
            -122.4194,
            37.3382,
            -121.8863
        );

        Ride ride = service.requestRide(command, "idemp_abc");
        
        Ride acceptedRide = service.acceptRide(ride.rideId, "driver_456", "acc_idemp_1");

        assertEquals(ride.rideId, acceptedRide.rideId);
        assertEquals("rider_123", acceptedRide.riderId);
        assertEquals("driver_456", acceptedRide.driverId);
        assertEquals(RideState.MATCHED, acceptedRide.state);

        Optional<Ride> fetchedRide = service.getRide(ride.rideId);
        assertTrue(fetchedRide.isPresent());
        assertEquals(acceptedRide, fetchedRide.get());
    }

    @Test
    void testUpdateRideStateTransitionsStateCorrectly() {
        RideService service = new InMemoryRideService();
        RequestRideCommand command = new RequestRideCommand(
            "rider_123",
            37.7749,
            -122.4194,
            37.3382,
            -121.8863
        );

        Ride ride = service.requestRide(command, "idemp_abc");
        service.acceptRide(ride.rideId, "driver_456", "acc_idemp_1");

        Ride enRouteRide = service.updateRideState(ride.rideId, RideState.DRIVER_EN_ROUTE);
        assertEquals(RideState.DRIVER_EN_ROUTE, enRouteRide.state);

        Ride inProgressRide = service.updateRideState(ride.rideId, RideState.IN_PROGRESS);
        assertEquals(RideState.IN_PROGRESS, inProgressRide.state);

        Ride completedRide = service.updateRideState(ride.rideId, RideState.COMPLETED);
        assertEquals(RideState.COMPLETED, completedRide.state);

        Optional<Ride> fetchedRide = service.getRide(ride.rideId);
        assertTrue(fetchedRide.isPresent());
        assertEquals(RideState.COMPLETED, fetchedRide.get().state);
    }
}
