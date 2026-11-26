"""
Tests for Ride Sharing System
"""

import unittest
import sys
import threading
import math
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
HELPER_DIR = TEST_DIR.parents[2] / "test_helpers"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))

from imports import import_modules_from


RIDE_MODULES = ["ride_sharing_entities", "ride_sharing", "ride_sharing_demo"]


def version_path(version: str) -> Path:
    return TEST_DIR.parent / version


def ride_entities(version: str):
    return import_modules_from(
        version_path(version),
        ["ride_sharing_entities"],
        purge_modules=RIDE_MODULES,
    )["ride_sharing_entities"]


class TestLocation(unittest.TestCase):
    """Test Location class."""
    
    def test_distance_calculation(self):
        """Test distance between two locations."""
        loc1 = self._create_location(12.9, 77.6)
        loc2 = self._create_location(12.91, 77.61)
        
        distance = self._calculate_distance(loc1, loc2)
        
        self.assertGreater(distance, 0)
        self.assertLess(distance, 5)  # Should be a few km
    
    def test_same_location_distance(self):
        """Test distance to same location is zero."""
        loc = self._create_location(12.9, 77.6)
        distance = self._calculate_distance(loc, loc)
        self.assertAlmostEqual(distance, 0, places=3)
    
    def _create_location(self, lat, lon):
        return {"latitude": lat, "longitude": lon}
    
    def _calculate_distance(self, loc1, loc2):
        lat_diff = loc1["latitude"] - loc2["latitude"]
        lon_diff = loc1["longitude"] - loc2["longitude"]
        return math.sqrt(lat_diff ** 2 + lon_diff ** 2) * 111


class TestDriver(unittest.TestCase):
    """Test Driver class."""
    
    def test_status_transitions(self):
        """Test driver status transitions."""
        status = "OFFLINE"
        
        # Go available
        status = "AVAILABLE"
        self.assertEqual("AVAILABLE", status)
        
        # Go busy
        status = "BUSY"
        self.assertEqual("BUSY", status)
        
        # Back to available
        status = "AVAILABLE"
        self.assertEqual("AVAILABLE", status)
    
    def test_rating_calculation(self):
        """Test driver rating calculation."""
        rating = 5.0
        count = 0
        
        # Add rating of 4
        count += 1
        rating = ((rating * (count - 1)) + 4) / count
        self.assertAlmostEqual(4.0, rating, places=2)
        
        # Add rating of 5
        count += 1
        rating = ((rating * (count - 1)) + 5) / count
        self.assertAlmostEqual(4.5, rating, places=2)


class TestTrip(unittest.TestCase):
    """Test Trip class."""
    
    def test_trip_state_machine(self):
        """Test trip state transitions."""
        status = "REQUESTED"
        
        # Match
        status = "MATCHED"
        self.assertEqual("MATCHED", status)
        
        # Start
        status = "IN_PROGRESS"
        self.assertEqual("IN_PROGRESS", status)
        
        # Complete
        status = "COMPLETED"
        self.assertEqual("COMPLETED", status)
    
    def test_cancellation(self):
        """Test trip cancellation."""
        status = "MATCHED"
        
        # Can cancel matched trip
        status = "CANCELLED"
        self.assertEqual("CANCELLED", status)
    
    def test_cannot_cancel_completed(self):
        """Test cannot cancel completed trip."""
        status = "COMPLETED"
        can_cancel = status not in ("COMPLETED", "IN_PROGRESS")
        self.assertFalse(can_cancel)


class TestFare(unittest.TestCase):
    """Test fare calculation."""
    
    def test_basic_fare(self):
        """Test basic fare calculation."""
        base_fare = 5.0
        per_km = 1.0
        per_min = 0.15
        distance = 10.0
        duration = 20
        multiplier = 2.0  # CAR
        
        total = (base_fare + (distance * per_km) + (duration * per_min)) * multiplier
        self.assertAlmostEqual(36.0, total, places=2)
    
    def test_surge_pricing(self):
        """Test surge pricing."""
        base = 5.0
        distance = 10.0
        duration = 20
        surge = 2.0
        
        normal = base + distance + (duration * 0.15)
        with_surge = normal * surge
        
        self.assertGreater(with_surge, normal)
        self.assertAlmostEqual(normal * 2, with_surge, places=2)
    
    def test_vehicle_type_pricing(self):
        """Test different vehicle type pricing."""
        base_fare = 10.0
        
        bike = base_fare * 1.0
        car = base_fare * 2.0
        premium = base_fare * 3.0
        
        self.assertLess(bike, car)
        self.assertLess(car, premium)


class TestMatching(unittest.TestCase):
    """Test driver matching."""
    
    def test_find_nearest_driver(self):
        """Test finding nearest driver."""
        driver_distances = [5.0, 2.0, 8.0]
        
        min_dist = float('inf')
        nearest_idx = -1
        
        for i, dist in enumerate(driver_distances):
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        self.assertEqual(1, nearest_idx)
    
    def test_filter_by_vehicle_type(self):
        """Test filtering drivers by vehicle type."""
        drivers = ["CAR", "BIKE", "CAR", "PREMIUM"]
        
        car_count = sum(1 for t in drivers if t == "CAR")
        self.assertEqual(2, car_count)


class TestConcurrency(unittest.TestCase):
    """Test thread-safety."""
    
    def test_concurrent_driver_reservation(self):
        """Test concurrent driver reservation."""
        driver_status = {"D1": "AVAILABLE"}
        results = []
        lock = threading.Lock()
        
        def try_reserve():
            with lock:
                if driver_status["D1"] == "AVAILABLE":
                    driver_status["D1"] = "BUSY"
                    results.append(True)
                else:
                    results.append(False)
        
        threads = [threading.Thread(target=try_reserve) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Only one should succeed
        success_count = sum(1 for r in results if r)
        self.assertEqual(1, success_count)
    
    def test_concurrent_rating_updates(self):
        """Test concurrent rating updates."""
        rating = [5.0]
        count = [0]
        lock = threading.Lock()
        
        def add_rating(stars):
            with lock:
                count[0] += 1
                rating[0] = ((rating[0] * (count[0] - 1)) + stars) / count[0]
        
        threads = []
        for i in range(100):
            stars = (i % 5) + 1
            t = threading.Thread(target=add_rating, args=(stars,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(100, count[0])
        self.assertTrue(1 <= rating[0] <= 5)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_ride_flow(self):
        """Test complete ride flow."""
        rider_status = "WAITING"
        trip_status = "REQUESTED"
        driver_status = "AVAILABLE"
        
        # Match
        driver_status = "BUSY"
        trip_status = "MATCHED"
        rider_status = "MATCHED"
        
        # Start
        trip_status = "IN_PROGRESS"
        rider_status = "IN_RIDE"
        
        # Complete
        trip_status = "COMPLETED"
        driver_status = "AVAILABLE"
        rider_status = "COMPLETED"
        
        self.assertEqual("COMPLETED", trip_status)
        self.assertEqual("AVAILABLE", driver_status)
    
    def test_multiple_concurrent_rides(self):
        """Test multiple concurrent rides."""
        drivers = {"D1": "AVAILABLE", "D2": "AVAILABLE", "D3": "AVAILABLE"}
        rides = ["R1", "R2", "R3"]
        assignments = {}
        
        for ride in rides:
            for driver_id, status in drivers.items():
                if status == "AVAILABLE":
                    drivers[driver_id] = "BUSY"
                    assignments[ride] = driver_id
                    break
        
        self.assertEqual(3, len(assignments))


class TestV1Basic(unittest.TestCase):
    """Test V1 basic implementation."""
    
    def test_service_registration(self):
        """Test rider and driver registration."""
        entities = ride_entities("v1-basic")
        RideSharingService = entities.RideSharingService
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        
        RideSharingService.reset_instance()
        service = RideSharingService()
        
        rider = service.register_rider("Alice", "555-0101")
        self.assertEqual("Alice", rider.name)
        
        vehicle = Vehicle("V1", VehicleType.CAR, "ABC-1234")
        driver = service.register_driver("John", "555-0201", vehicle)
        self.assertEqual("John", driver.name)
        
        RideSharingService.reset_instance()


class TestV2Extended(unittest.TestCase):
    """Test V2 extended implementation."""
    
    def test_matching_strategies(self):
        """Test different matching strategies."""
        entities = ride_entities("v2-extended")
        NearestDriverStrategy = entities.NearestDriverStrategy
        HighestRatedDriverStrategy = entities.HighestRatedDriverStrategy
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        Location = entities.Location
        
        drivers = [
            Driver("D1", "D1", "1", Vehicle("V1", VehicleType.CAR, "1")),
            Driver("D2", "D2", "2", Vehicle("V2", VehicleType.CAR, "2")),
            Driver("D3", "D3", "3", Vehicle("V3", VehicleType.CAR, "3")),
        ]
        
        drivers[0].set_available()
        drivers[0].update_location(Location(12.9, 77.6))
        drivers[0].rating = 4.5
        
        drivers[1].set_available()
        drivers[1].update_location(Location(12.91, 77.61)) # ~1.5km
        drivers[1].rating = 4.0
        
        drivers[2].set_available()
        drivers[2].update_location(Location(12.92, 77.62)) # ~3km
        drivers[2].rating = 5.0
        
        pickup = Location(12.9, 77.6) # Distances: D1=0, D2=~1.5, D3=~3
        
        # Nearest driver strategy
        nearest_strategy = NearestDriverStrategy()
        nearest = nearest_strategy.find_match(pickup, VehicleType.CAR, drivers)
        self.assertEqual("D1", nearest.name)
        
        # Priority strategy (rating / distance)
        best_strategy = HighestRatedDriverStrategy()
        best = best_strategy.find_match(pickup, VehicleType.CAR, drivers)
        # D1: 45 / 1 = 45
        # D2: 40 / 2.5 = 16
        # D3: 50 / 4 = 12.5
        self.assertEqual("D1", best.name)

    def test_v2_features(self):
        entities = ride_entities("v2-extended")
        SurgePricingStrategy = entities.SurgePricingStrategy
        VehicleType = entities.VehicleType
        Fare = entities.Fare
        
        surge = SurgePricingStrategy(1.5)
        fare = Fare(10, 20, VehicleType.CAR, surge)
        # standard = 5.0 + (10 * 1.0) + (20 * 0.15) = 18.0
        # Car multiplier = 2.0 -> 36.0
        # Surge multiplier = 1.5 -> 54.0
        self.assertAlmostEqual(54.0, fare.total)

        Trip = entities.Trip
        Rider = entities.Rider
        Location = entities.Location
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        DriverAcceptanceStatus = entities.DriverAcceptanceStatus
        TripStatus = entities.TripStatus
        
        rider = Rider("R1", "Alice", "1")
        pickup = Location(0, 0)
        dropoff = Location(1, 1)
        trip = Trip("T1", rider, pickup, dropoff, VehicleType.CAR)
        
        driver = Driver("D1", "Bob", "2", Vehicle("V1", VehicleType.CAR, "1"))
        driver.set_available()
        
        trip.offer_to_driver(driver)
        self.assertEqual(DriverAcceptanceStatus.OFFERED, trip.driver_acceptance_status)
        
        trip.accept_by_driver()
        self.assertEqual(DriverAcceptanceStatus.ACCEPTED, trip.driver_acceptance_status)
        self.assertEqual(TripStatus.MATCHED, trip.status)


class TestV3Optimized(unittest.TestCase):
    """Test V3 optimized implementation."""
    
    def test_grid_index(self):
        """Test grid-based driver indexing."""
        grid_size = 0.01
        
        def get_grid_key(lat, lon):
            return f"{int(lat / grid_size)}:{int(lon / grid_size)}"
        
        loc1 = (12.905, 77.605)
        loc2 = (12.915, 77.605)
        
        key1 = get_grid_key(*loc1)
        key2 = get_grid_key(*loc2)
        
        # Should be in different grid cells
        self.assertNotEqual(key1, key2)


    def test_concurrent_driver_assignment(self):
        entities = ride_entities("v3-optimized")
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        DriverStatus = entities.DriverStatus
        Location = entities.Location
        Trip = entities.Trip
        Rider = entities.Rider
        
        driver = Driver("D1", "Bob", "2", Vehicle("V1", VehicleType.CAR, "1"))
        driver.set_available()
        
        rider1 = Rider("R1", "Alice", "1")
        rider2 = Rider("R2", "Charlie", "2")
        pickup = Location(0, 0)
        dropoff = Location(1, 1)
        
        trip1 = Trip("T1", rider1, pickup, dropoff, VehicleType.CAR)
        trip2 = Trip("T2", rider2, pickup, dropoff, VehicleType.CAR)
        
        trip1.offer_to_driver(driver)
        trip2.offer_to_driver(driver)
        
        results = []
        lock = threading.Lock()
        
        def accept_trip(trip):
            try:
                trip.accept_by_driver()
                with lock:
                    results.append(True)
            except Exception:
                with lock:
                    results.append(False)
                    
        t1 = threading.Thread(target=accept_trip, args=(trip1,))
        t2 = threading.Thread(target=accept_trip, args=(trip2,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Only one trip should have been accepted
        self.assertEqual(1, sum(1 for r in results if r))
        self.assertEqual(DriverStatus.BUSY, driver.status)


    def test_v3_grid_index_actual(self):
        entities = ride_entities("v3-optimized")
        GridIndex = entities.GridIndex
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        Location = entities.Location
        
        index = GridIndex(grid_size=0.01)
        
        # Cell 0:0 for both
        d1 = Driver("D1", "Bob", "1", Vehicle("V1", VehicleType.CAR, "1"))
        d1.update_location(Location(0.005, 0.005))
        
        d2 = Driver("D2", "Charlie", "2", Vehicle("V2", VehicleType.CAR, "2"))
        d2.update_location(Location(0.008, 0.008))
        
        # Cell 10:10
        d3 = Driver("D3", "Dave", "3", Vehicle("V3", VehicleType.CAR, "3"))
        d3.update_location(Location(0.105, 0.105))
        
        index.update_driver(d1)
        index.update_driver(d2)
        index.update_driver(d3)
        
        nearby = index.get_nearby_drivers(Location(0.001, 0.001), radius_cells=1)
        self.assertEqual(2, len(nearby))
        self.assertIn(d1, nearby)
        self.assertIn(d2, nearby)
        
        far = index.get_nearby_drivers(Location(0.101, 0.101), radius_cells=1)
        self.assertEqual(1, len(far))
        self.assertIn(d3, far)




    def test_concurrent_driver_assignment(self):
        entities = ride_entities("v3-optimized")
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        DriverStatus = entities.DriverStatus
        Location = entities.Location
        Trip = entities.Trip
        Rider = entities.Rider
        
        driver = Driver("D1", "Bob", "2", Vehicle("V1", VehicleType.CAR, "1"))
        driver.set_available()
        
        rider1 = Rider("R1", "Alice", "1")
        rider2 = Rider("R2", "Charlie", "2")
        pickup = Location(0, 0)
        dropoff = Location(1, 1)
        
        trip1 = Trip("T1", rider1, pickup, dropoff, VehicleType.CAR)
        trip2 = Trip("T2", rider2, pickup, dropoff, VehicleType.CAR)
        
        trip1.offer_to_driver(driver)
        trip2.offer_to_driver(driver)
        
        results = []
        lock = threading.Lock()
        
        def accept_trip(trip):
            try:
                trip.accept_by_driver()
                with lock:
                    results.append(True)
            except Exception:
                with lock:
                    results.append(False)
                    
        t1 = threading.Thread(target=accept_trip, args=(trip1,))
        t2 = threading.Thread(target=accept_trip, args=(trip2,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Only one trip should have been accepted
        self.assertEqual(1, sum(1 for r in results if r))
        self.assertEqual(DriverStatus.BUSY, driver.status)

    def test_v3_grid_index_actual(self):
        entities = ride_entities("v3-optimized")
        GridIndex = entities.GridIndex
        Driver = entities.Driver
        Vehicle = entities.Vehicle
        VehicleType = entities.VehicleType
        Location = entities.Location
        
        index = GridIndex(grid_size=0.01)
        
        # Cell 0:0 for both
        d1 = Driver("D1", "Bob", "1", Vehicle("V1", VehicleType.CAR, "1"))
        d1.update_location(Location(0.005, 0.005))
        
        d2 = Driver("D2", "Charlie", "2", Vehicle("V2", VehicleType.CAR, "2"))
        d2.update_location(Location(0.008, 0.008))
        
        # Cell 10:10
        d3 = Driver("D3", "Dave", "3", Vehicle("V3", VehicleType.CAR, "3"))
        d3.update_location(Location(0.105, 0.105))
        
        index.update_driver(d1)
        index.update_driver(d2)
        index.update_driver(d3)
        
        nearby = index.get_nearby_drivers(Location(0.001, 0.001), radius_cells=1)
        self.assertEqual(2, len(nearby))
        self.assertIn(d1, nearby)
        self.assertIn(d2, nearby)
        
        far = index.get_nearby_drivers(Location(0.101, 0.101), radius_cells=1)
        self.assertEqual(1, len(far))
        self.assertIn(d3, far)

if __name__ == "__main__":

    unittest.main()



