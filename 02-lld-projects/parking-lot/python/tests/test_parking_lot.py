"""
Tests for Parking Lot System
"""
import unittest
import sys
import os
import threading
import time

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))


class TestV1BasicParkingLot(unittest.TestCase):
    """Tests for V1 Basic Parking Lot"""
    
    def setUp(self):
        from parking_lot import ParkingLot
        ParkingLot.reset_instance()
    
    def tearDown(self):
        from parking_lot import ParkingLot
        ParkingLot.reset_instance()
    
    def test_vehicle_factory_creates_correct_types(self):
        """Vehicle factory should create correct vehicle types"""
        from vehicle import VehicleFactory, VehicleType
        
        motorcycle = VehicleFactory.create_vehicle(VehicleType.MOTORCYCLE, "M-001")
        car = VehicleFactory.create_vehicle(VehicleType.CAR, "C-001")
        truck = VehicleFactory.create_vehicle(VehicleType.TRUCK, "T-001")
        
        self.assertEqual(motorcycle.vehicle_type, VehicleType.MOTORCYCLE)
        self.assertEqual(car.vehicle_type, VehicleType.CAR)
        self.assertEqual(truck.vehicle_type, VehicleType.TRUCK)
    
    def test_motorcycle_spot_fits_only_motorcycles(self):
        """Motorcycle spot should only fit motorcycles"""
        from parking_spot import ParkingSpot, SpotType
        from vehicle import Motorcycle, Car, Truck
        
        spot = ParkingSpot("F1-M001", SpotType.MOTORCYCLE_SPOT, 1)
        
        motorcycle = Motorcycle("M-001")
        car = Car("C-001")
        truck = Truck("T-001")
        
        self.assertTrue(spot.can_fit(motorcycle))
        self.assertFalse(spot.can_fit(car))
        self.assertFalse(spot.can_fit(truck))
    
    def test_compact_spot_fits_motorcycles_and_cars(self):
        """Compact spot should fit motorcycles and cars"""
        from parking_spot import ParkingSpot, SpotType
        from vehicle import Motorcycle, Car, Truck
        
        spot = ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1)
        
        motorcycle = Motorcycle("M-001")
        car = Car("C-001")
        truck = Truck("T-001")
        
        self.assertTrue(spot.can_fit(motorcycle))
        self.assertTrue(spot.can_fit(car))
        self.assertFalse(spot.can_fit(truck))
    
    def test_large_spot_fits_all_vehicles(self):
        """Large spot should fit all vehicle types"""
        from parking_spot import ParkingSpot, SpotType
        from vehicle import Motorcycle, Car, Truck
        
        spot = ParkingSpot("F1-L001", SpotType.LARGE_SPOT, 1)
        
        motorcycle = Motorcycle("M-001")
        car = Car("C-001")
        truck = Truck("T-001")
        
        self.assertTrue(spot.can_fit(motorcycle))
        self.assertTrue(spot.can_fit(car))
        self.assertTrue(spot.can_fit(truck))
    
    def test_park_and_unpark(self):
        """Parking and unparking should work correctly"""
        from parking_spot import ParkingSpot, SpotType
        from vehicle import Car
        
        spot = ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1)
        car = Car("C-001")
        
        self.assertTrue(spot.is_available)
        self.assertTrue(spot.park(car))
        self.assertFalse(spot.is_available)
        self.assertTrue(spot.is_occupied)
        
        unparked = spot.unpark()
        self.assertEqual(unparked.license_plate, car.license_plate)
        self.assertTrue(spot.is_available)
    
    def test_cannot_park_in_occupied_spot(self):
        """Should not be able to park in occupied spot"""
        from parking_spot import ParkingSpot, SpotType
        from vehicle import Car
        
        spot = ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1)
        car1 = Car("C-001")
        car2 = Car("C-002")
        
        self.assertTrue(spot.park(car1))
        self.assertFalse(spot.park(car2))
    
    def test_parking_lot_singleton(self):
        """ParkingLot should be a singleton"""
        from parking_lot import ParkingLot
        
        lot1 = ParkingLot.get_instance()
        lot2 = ParkingLot.get_instance()
        
        self.assertIs(lot1, lot2)
    
    def test_parking_lot_parks_vehicle(self):
        """ParkingLot should park vehicle and return ticket"""
        from parking_lot import ParkingLot
        from vehicle import Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        car = Car("C-001")
        ticket = lot.park_vehicle(car)
        
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.license_plate, car.license_plate)
    
    def test_prevents_double_parking(self):
        """ParkingLot should prevent double parking"""
        from parking_lot import ParkingLot
        from vehicle import Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        car = Car("C-001")
        ticket1 = lot.park_vehicle(car)
        ticket2 = lot.park_vehicle(car)
        
        self.assertIsNotNone(ticket1)
        self.assertIsNone(ticket2)
    
    def test_unpark_calculates_fee(self):
        """Unparking should calculate fee"""
        from parking_lot import ParkingLot
        from vehicle import Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        car = Car("C-001")
        ticket = lot.park_vehicle(car)
        fee = lot.unpark_vehicle(ticket)
        
        self.assertGreaterEqual(fee, 0)
        self.assertIsNone(lot.find_vehicle("C-001"))
    
    def test_find_vehicle(self):
        """ParkingLot should find vehicle by license plate"""
        from parking_lot import ParkingLot
        from vehicle import Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        car = Car("C-001")
        lot.park_vehicle(car)
        
        spot = lot.find_vehicle("C-001")
        self.assertIsNotNone(spot)
        self.assertEqual(spot.vehicle.license_plate, "C-001")
    
    def test_available_spot_count(self):
        """ParkingLot should return correct available spot count"""
        from parking_lot import ParkingLot
        from vehicle import VehicleType, Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)  # 5 motorcycle, 10 compact, 3 large
        
        # Cars can use compact + large = 13
        self.assertEqual(lot.get_available_spots(VehicleType.CAR), 13)
        
        car = Car("C-001")
        lot.park_vehicle(car)
        
        self.assertEqual(lot.get_available_spots(VehicleType.CAR), 12)
    
    def test_ticket_minimum_duration(self):
        """Ticket duration should be at least 1 hour"""
        from parking_lot import ParkingLot
        from vehicle import Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        car = Car("C-001")
        ticket = lot.park_vehicle(car)
        
        self.assertGreaterEqual(ticket.get_duration_hours(), 1)


class TestV2ExtendedParkingLot(unittest.TestCase):
    """Tests for V2 Extended Parking Lot"""
    
    def setUp(self):
        # Import from v2-extended
        v2_path = os.path.join(os.path.dirname(__file__), '..', 'v2-extended')
        sys.path.insert(0, v2_path)
        import importlib
        # Clear cached modules so importlib loads from v2-extended
        for mod_name in ['parking_lot', 'parking_spot', 'ticket', 'vehicle', 'floor']:
            sys.modules.pop(mod_name, None)
        self.parking_lot_module = importlib.import_module('parking_lot')
        self.parking_lot_module.ParkingLot.reset_instance()
    
    def tearDown(self):
        self.parking_lot_module.ParkingLot.reset_instance()
    
    def test_reservation_works(self):
        """Should be able to reserve a spot"""
        ParkingLot = self.parking_lot_module.ParkingLot
        VehicleType = self.parking_lot_module.VehicleType
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 5)
        
        spot = lot.reserve_spot("VIP-001", VehicleType.CAR)
        self.assertIsNotNone(spot)
        self.assertTrue(spot.is_reserved)
    
    def test_vip_parks_in_reserved_spot(self):
        """VIP should park in reserved spot"""
        ParkingLot = self.parking_lot_module.ParkingLot
        VehicleType = self.parking_lot_module.VehicleType
        Car = self.parking_lot_module.Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 5)
        
        reserved_spot = lot.reserve_spot("VIP-001", VehicleType.CAR)
        
        vip_car = Car("VIP-001")
        ticket = lot.park_vehicle(vip_car)
        
        self.assertIsNotNone(ticket)
        self.assertTrue(ticket.is_reservation)
        self.assertEqual(ticket.spot.spot_id, reserved_spot.spot_id)
    
    def test_payment_processing(self):
        """Payment should be processed correctly"""
        ParkingLot = self.parking_lot_module.ParkingLot
        PaymentMethod = self.parking_lot_module.PaymentMethod
        Car = self.parking_lot_module.Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 5)
        
        car = Car("C-001")
        ticket = lot.park_vehicle(car)
        
        payment = lot.unpark_vehicle(ticket, PaymentMethod.CREDIT_CARD)
        
        self.assertIsNotNone(payment)
        self.assertGreater(payment.amount, 0)


class TestV3ConcurrentParkingLot(unittest.TestCase):
    """Tests for V3 Concurrent Parking Lot"""
    
    def setUp(self):
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        import importlib
        # Clear cached modules so importlib loads from v3-optimized
        for mod_name in ['parking_lot', 'parking_spot', 'ticket', 'vehicle', 'floor']:
            sys.modules.pop(mod_name, None)
        self.parking_lot_module = importlib.import_module('parking_lot')
        self.parking_lot_module.ParkingLot.reset_instance()
    
    def tearDown(self):
        self.parking_lot_module.ParkingLot.reset_instance()
    
    def test_concurrent_parking(self):
        """Multiple threads should be able to park concurrently"""
        ParkingLot = self.parking_lot_module.ParkingLot
        Car = self.parking_lot_module.Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(10, 30, 10)
        
        tickets = []
        lock = threading.Lock()
        
        def park_worker(thread_id):
            for i in range(5):
                car = Car(f"T{thread_id}-V{i:03d}")
                ticket = lot.park_vehicle(car)
                if ticket:
                    with lock:
                        tickets.append(ticket)
        
        threads = []
        for t in range(8):
            thread = threading.Thread(target=park_worker, args=(t,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have parked all 40 vehicles
        self.assertEqual(len(tickets), 40)
        self.assertEqual(lot.active_vehicle_count, 40)
    
    def test_no_double_parking_concurrent(self):
        """No double parking even with concurrent attempts"""
        ParkingLot = self.parking_lot_module.ParkingLot
        Car = self.parking_lot_module.Car
        
        lot = ParkingLot.get_instance()
        lot.add_floor(10, 30, 10)
        
        successful = [0]
        lock = threading.Lock()
        
        def try_park_same_car():
            car = Car("SAME-001")
            ticket = lot.park_vehicle(car)
            if ticket:
                with lock:
                    successful[0] += 1
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=try_park_same_car)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one should succeed
        self.assertEqual(successful[0], 1)
        self.assertEqual(lot.active_vehicle_count, 1)


class TestPricingStrategies(unittest.TestCase):
    """Tests for pricing strategies"""
    
    def test_hourly_pricing_by_vehicle_type(self):
        """Hourly pricing should charge differently by vehicle type"""
        from parking_lot import ParkingLot, HourlyPricing
        from vehicle import Motorcycle, Car, Truck
        
        ParkingLot.reset_instance()
        lot = ParkingLot.get_instance()
        lot.add_floor(5, 10, 3)
        
        pricing = HourlyPricing()
        
        moto = Motorcycle("M-001")
        car = Car("C-001")
        truck = Truck("T-001")
        
        moto_ticket = lot.park_vehicle(moto)
        car_ticket = lot.park_vehicle(car)
        truck_ticket = lot.park_vehicle(truck)
        
        # For 1 hour
        moto_fee = pricing.calculate_fee(moto_ticket)
        car_fee = pricing.calculate_fee(car_ticket)
        truck_fee = pricing.calculate_fee(truck_ticket)
        
        self.assertEqual(moto_fee, 1.0)  # $1/hour
        self.assertEqual(car_fee, 2.0)   # $2/hour
        self.assertEqual(truck_fee, 4.0) # $4/hour
        
        ParkingLot.reset_instance()


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow"""
    
    def test_full_workflow(self):
        """Test complete parking workflow"""
        from parking_lot import ParkingLot
        from vehicle import Motorcycle, Car, Truck, VehicleType
        
        ParkingLot.reset_instance()
        lot = ParkingLot.get_instance("Test Lot")
        lot.add_floor(2, 3, 1)
        
        # Park vehicles
        moto = Motorcycle("M-001")
        car1 = Car("C-001")
        car2 = Car("C-002")
        truck = Truck("T-001")
        
        moto_ticket = lot.park_vehicle(moto)
        car1_ticket = lot.park_vehicle(car1)
        car2_ticket = lot.park_vehicle(car2)
        truck_ticket = lot.park_vehicle(truck)
        
        self.assertIsNotNone(moto_ticket)
        self.assertIsNotNone(car1_ticket)
        self.assertIsNotNone(car2_ticket)
        self.assertIsNotNone(truck_ticket)
        
        self.assertEqual(lot.active_vehicle_count, 4)
        
        # Unpark one car
        fee = lot.unpark_vehicle(car1_ticket)
        self.assertGreaterEqual(fee, 0)
        self.assertEqual(lot.active_vehicle_count, 3)
        
        # Park another car in freed spot
        car3 = Car("C-003")
        car3_ticket = lot.park_vehicle(car3)
        self.assertIsNotNone(car3_ticket)
        
        # Cannot park same car twice
        duplicate = lot.park_vehicle(car2)
        self.assertIsNone(duplicate)
        
        ParkingLot.reset_instance()


if __name__ == "__main__":
    unittest.main()
