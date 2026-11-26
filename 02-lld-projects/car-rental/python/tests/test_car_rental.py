"""
Car Rental System - Tests
"""

import unittest
import sys
import os
from datetime import date, timedelta

# Add v1-basic to path — directory names with hyphens cannot be used as Python
# package imports directly, so sys.path manipulation is required here.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))

from car_rental import (
    Vehicle, Customer, Reservation, RentalService,
    VehicleType, VehicleStatus, ReservationStatus,
)


class TestVehicle(unittest.TestCase):

    def test_vehicle_creation(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.assertEqual("V1", v.vehicle_id)
        self.assertTrue(v.is_available())
        self.assertEqual(50.0, v.price_per_day)

    def test_vehicle_reserve_and_rent(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        v.reserve()
        self.assertEqual(VehicleStatus.RESERVED, v.status)
        v.start_rental()
        self.assertEqual(VehicleStatus.RENTED, v.status)
        v.complete_rental()
        self.assertEqual(VehicleStatus.AVAILABLE, v.status)

    def test_cannot_reserve_rented_vehicle(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        v.reserve()
        v.start_rental()
        # Reserving a rented vehicle should have no effect
        v.reserve()
        self.assertEqual(VehicleStatus.RENTED, v.status)


class TestReservation(unittest.TestCase):

    def test_cost_calculation(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        c = Customer("C1", "Alice", "alice@test.com", "DL-001")
        start = date.today()
        end = start + timedelta(days=3)
        r = Reservation(c, v, start, end)
        self.assertEqual(150.0, r.total_cost)

    def test_single_day_minimum(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        c = Customer("C1", "Alice", "alice@test.com", "DL-001")
        today = date.today()
        r = Reservation(c, v, today, today)
        self.assertEqual(50.0, r.total_cost)

    def test_reservation_lifecycle(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        c = Customer("C1", "Alice", "alice@test.com", "DL-001")
        start = date.today()
        end = start + timedelta(days=2)
        r = Reservation(c, v, start, end)

        self.assertEqual(ReservationStatus.PENDING, r.status)
        r.confirm()
        self.assertEqual(ReservationStatus.CONFIRMED, r.status)
        r.start_rental()
        self.assertEqual(ReservationStatus.ACTIVE, r.status)
        r.complete()
        self.assertEqual(ReservationStatus.COMPLETED, r.status)
        self.assertTrue(v.is_available())

    def test_cancel_reservation(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        c = Customer("C1", "Alice", "alice@test.com", "DL-001")
        r = Reservation(c, v, date.today(), date.today() + timedelta(days=1))
        r.confirm()
        r.cancel()
        self.assertEqual(ReservationStatus.CANCELLED, r.status)
        self.assertTrue(v.is_available())


class TestRentalService(unittest.TestCase):

    def setUp(self):
        RentalService.reset_instance()
        Reservation._counter = 0
        self.service = RentalService()

    def test_singleton(self):
        s2 = RentalService()
        self.assertIs(self.service, s2)

    def test_add_and_search_vehicles(self):
        self.service.add_vehicle(
            Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0))
        self.service.add_vehicle(
            Vehicle("V2", "DEF-456", "Ford", "Explorer", VehicleType.SUV, 80.0))

        cars = self.service.search_available(VehicleType.CAR)
        self.assertEqual(1, len(cars))
        suvs = self.service.search_available(VehicleType.SUV)
        self.assertEqual(1, len(suvs))

    def test_make_reservation(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.service.add_vehicle(v)
        c = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")

        start = date.today()
        end = start + timedelta(days=3)
        res = self.service.make_reservation(c, v, start, end)

        self.assertEqual(ReservationStatus.CONFIRMED, res.status)
        self.assertEqual(150.0, res.total_cost)
        self.assertFalse(v.is_available())

    def test_full_rental_workflow(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.service.add_vehicle(v)
        c = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")

        res = self.service.make_reservation(
            c, v, date.today(), date.today() + timedelta(days=2))
        self.service.pickup_vehicle(res)
        self.assertEqual(ReservationStatus.ACTIVE, res.status)

        self.service.return_vehicle(res)
        self.assertEqual(ReservationStatus.COMPLETED, res.status)
        self.assertTrue(v.is_available())

    def test_cannot_reserve_unavailable(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.service.add_vehicle(v)
        c = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")

        self.service.make_reservation(
            c, v, date.today(), date.today() + timedelta(days=1))

        with self.assertRaises(ValueError):
            self.service.make_reservation(
                c, v, date.today(), date.today() + timedelta(days=1))

    def test_cancel_and_rebook(self):
        v = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.service.add_vehicle(v)
        c = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")

        res = self.service.make_reservation(
            c, v, date.today(), date.today() + timedelta(days=1))
        self.service.cancel_reservation(res)
        self.assertTrue(v.is_available())

        # Rebook same vehicle
        res2 = self.service.make_reservation(
            c, v, date.today(), date.today() + timedelta(days=2))
        self.assertEqual(ReservationStatus.CONFIRMED, res2.status)


if __name__ == '__main__':
    unittest.main()
