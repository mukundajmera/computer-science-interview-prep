"""
Car Rental System - V1 Basic
Core implementation with vehicles, customers, and reservations.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional


class VehicleType(Enum):
    CAR = "car"
    SUV = "suv"
    TRUCK = "truck"
    VAN = "van"
    LUXURY = "luxury"


class VehicleStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    RENTED = "rented"
    MAINTENANCE = "maintenance"


class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Vehicle:
    def __init__(self, vehicle_id: str, license_plate: str, make: str,
                 model: str, vehicle_type: VehicleType, price_per_day: float):
        self.vehicle_id = vehicle_id
        self.license_plate = license_plate
        self.make = make
        self.model = model
        self.vehicle_type = vehicle_type
        self.status = VehicleStatus.AVAILABLE
        self.price_per_day = price_per_day

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def reserve(self) -> None:
        if self.status == VehicleStatus.AVAILABLE:
            self.status = VehicleStatus.RESERVED

    def start_rental(self) -> None:
        if self.status == VehicleStatus.RESERVED:
            self.status = VehicleStatus.RENTED

    def complete_rental(self) -> None:
        self.status = VehicleStatus.AVAILABLE

    def release(self) -> None:
        self.status = VehicleStatus.AVAILABLE

    def __str__(self) -> str:
        return f"{self.make} {self.model} ({self.vehicle_type.value}) - ${self.price_per_day}/day"


class Customer:
    def __init__(self, customer_id: str, name: str, email: str, driving_license: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.driving_license = driving_license
        self.reservations: List['Reservation'] = []

    def add_reservation(self, reservation: 'Reservation') -> None:
        self.reservations.append(reservation)

    def get_active_reservations(self) -> List['Reservation']:
        return [r for r in self.reservations
                if r.status in (ReservationStatus.CONFIRMED, ReservationStatus.ACTIVE)]


class Reservation:
    _counter = 0

    def __init__(self, customer: Customer, vehicle: Vehicle,
                 start_date: date, end_date: date):
        Reservation._counter += 1
        self.reservation_id = f"RES-{Reservation._counter}"
        self.customer = customer
        self.vehicle = vehicle
        self.start_date = start_date
        self.end_date = end_date
        self.status = ReservationStatus.PENDING
        self.total_cost = self._calculate_cost()

    def _calculate_cost(self) -> float:
        days = max(1, (self.end_date - self.start_date).days)
        return days * self.vehicle.price_per_day

    def confirm(self) -> None:
        if self.status == ReservationStatus.PENDING:
            self.status = ReservationStatus.CONFIRMED
            self.vehicle.reserve()

    def cancel(self) -> None:
        if self.status in (ReservationStatus.PENDING, ReservationStatus.CONFIRMED):
            self.status = ReservationStatus.CANCELLED
            self.vehicle.release()

    def start_rental(self) -> None:
        if self.status == ReservationStatus.CONFIRMED:
            self.status = ReservationStatus.ACTIVE
            self.vehicle.start_rental()

    def complete(self) -> None:
        if self.status == ReservationStatus.ACTIVE:
            self.status = ReservationStatus.COMPLETED
            self.vehicle.complete_rental()


class RentalService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.vehicles: dict[str, Vehicle] = {}
        self.customers: dict[str, Customer] = {}
        self.reservations: dict[str, Reservation] = {}
        self._initialized = True

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    def add_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicles[vehicle.vehicle_id] = vehicle

    def register_customer(self, customer_id: str, name: str,
                         email: str, driving_license: str) -> Customer:
        customer = Customer(customer_id, name, email, driving_license)
        self.customers[customer_id] = customer
        return customer

    def search_available(self, vehicle_type: VehicleType) -> List[Vehicle]:
        return [v for v in self.vehicles.values()
                if v.is_available() and v.vehicle_type == vehicle_type]

    def make_reservation(self, customer: Customer, vehicle: Vehicle,
                        start_date: date, end_date: date) -> Reservation:
        if not vehicle.is_available():
            raise ValueError("Vehicle is not available")

        reservation = Reservation(customer, vehicle, start_date, end_date)
        reservation.confirm()
        customer.add_reservation(reservation)
        self.reservations[reservation.reservation_id] = reservation
        return reservation

    def pickup_vehicle(self, reservation: Reservation) -> None:
        reservation.start_rental()

    def return_vehicle(self, reservation: Reservation) -> None:
        reservation.complete()

    def cancel_reservation(self, reservation: Reservation) -> None:
        reservation.cancel()

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        return self.vehicles.get(vehicle_id)

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        return self.reservations.get(reservation_id)
