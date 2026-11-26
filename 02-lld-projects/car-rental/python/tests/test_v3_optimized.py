import unittest
import sys
import importlib.util
from datetime import date, timedelta
from pathlib import Path

module_path = Path(__file__).parent.parent / "v3-optimized" / "car_rental.py"
spec = importlib.util.spec_from_file_location("car_rental_v3", module_path)
v3_module = importlib.util.module_from_spec(spec)
sys.modules["car_rental_v3"] = v3_module
spec.loader.exec_module(v3_module)

Vehicle = v3_module.Vehicle
VehicleType = v3_module.VehicleType
Customer = v3_module.Customer
RentalService = v3_module.RentalService
EquipmentType = v3_module.EquipmentType
ReservationStatus = v3_module.ReservationStatus

class TestV3Optimized(unittest.TestCase):

    def setUp(self):
        RentalService.reset_instance()
        self.service = RentalService()
        self.vehicle = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.customer = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")
        self.service.add_vehicle(self.vehicle)

    def test_dynamic_pricing_summer(self):
        start = date(2024, 6, 5) 
        end = start + timedelta(days=2) 
        
        res = self.service.make_reservation(self.customer, self.vehicle, start, end)
        self.assertEqual(150.0, res.total_cost)

    def test_dynamic_pricing_weekend(self):
        start = date(2024, 5, 4) 
        end = start + timedelta(days=2) 
        
        res = self.service.make_reservation(self.customer, self.vehicle, start, end)
        self.assertEqual(120.0, res.total_cost)

    def test_dynamic_pricing_mixed(self):
        start = date(2024, 5, 3)
        end = start + timedelta(days=2)
        
        res = self.service.make_reservation(self.customer, self.vehicle, start, end)
        self.assertEqual(110.0, res.total_cost)
        
    def test_v2_features_still_work(self):
        start = date(2024, 5, 1) # Wednesday
        end = start + timedelta(days=2) 
        
        res = self.service.make_reservation(
            self.customer, self.vehicle, start, end,
            equipments=[EquipmentType.CHILD_SEAT]
        )
        self.assertEqual(120.0, res.total_cost)
        
        self.service.pickup_vehicle(res)
        
        return_date = end + timedelta(days=1)
        self.service.return_vehicle(res, return_date=return_date)
        
        self.assertEqual(220.0, res.total_cost)

if __name__ == '__main__':
    unittest.main()
