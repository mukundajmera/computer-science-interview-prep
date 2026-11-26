"""Car Rental Python Module."""
from enum import Enum
from typing import Dict, List, Optional
from datetime import date

class VehicleType(Enum):
    CAR = ("CAR", 50.0)
    SUV = ("SUV", 80.0)
    VAN = ("VAN", 100.0)
    LUXURY = ("LUXURY", 150.0)
    def __init__(self, name, rate): self._rate = rate
    @property
    def daily_rate(self): return self._rate

class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Vehicle:
    def __init__(self, id: str, license_plate: str, vtype: VehicleType, make: str, model: str):
        self.id = id
        self.license_plate = license_plate
        self.type = vtype
        self.make = make
        self.model = model
        self.is_available = True
    @property
    def daily_rate(self): return self.type.daily_rate
    def __str__(self): return f"{self.make} {self.model} ({self.type.name}) - ${self.daily_rate}/day"

class Customer:
    def __init__(self, id: str, name: str, email: str, license: str):
        self.id = id
        self.name = name
        self.email = email
        self.drivers_license = license

class Reservation:
    def __init__(self, id: str, customer: Customer, vehicle: Vehicle, start: date, end: date):
        self.id = id
        self.customer = customer
        self.vehicle = vehicle
        self.start_date = start
        self.end_date = end
        self.status = ReservationStatus.PENDING
        self.total_cost = max(1, (end - start).days) * vehicle.daily_rate
    
    def confirm(self): self.status = ReservationStatus.CONFIRMED
    def pick_up(self): self.status = ReservationStatus.ACTIVE; self.vehicle.is_available = False
    def return_vehicle(self): self.status = ReservationStatus.COMPLETED; self.vehicle.is_available = True

class RentalService:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.vehicles: Dict[str, Vehicle] = {}
            cls._instance.customers: Dict[str, Customer] = {}
            cls._instance.reservations: Dict[str, Reservation] = {}
            cls._instance._counter = 0
        return cls._instance
    
    def add_vehicle(self, v: Vehicle): self.vehicles[v.id] = v
    def register_customer(self, c: Customer): self.customers[c.id] = c
    
    def search_available(self, vtype: Optional[VehicleType] = None) -> List[Vehicle]:
        return [v for v in self.vehicles.values() if v.is_available and (vtype is None or v.type == vtype)]
    
    def make_reservation(self, cust_id: str, veh_id: str, start: date, end: date):
        customer = self.customers.get(cust_id)
        vehicle = self.vehicles.get(veh_id)
        if not customer or not vehicle or not vehicle.is_available: return None
        self._counter += 1
        res = Reservation(f"RES-{self._counter}", customer, vehicle, start, end)
        self.reservations[res.id] = res
        res.confirm()
        print(f"Reservation: {res.id} - ${res.total_cost:.2f}")
        return res
    
    def return_vehicle(self, res_id: str):
        res = self.reservations.get(res_id)
        if res:
            res.return_vehicle()
            print(f"Returned. Total: ${res.total_cost:.2f}")
