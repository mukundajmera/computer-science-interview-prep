import unittest
import sys
import importlib.util
from datetime import date, timedelta
from pathlib import Path

# Load module dynamically because directory name contains hyphen
module_path = Path(__file__).parent.parent / "v2-extended" / "car_rental.py"
spec = importlib.util.spec_from_file_location("car_rental_v2", module_path)
v2_module = importlib.util.module_from_spec(spec)
sys.modules["car_rental_v2"] = v2_module
spec.loader.exec_module(v2_module)

Vehicle = v2_module.Vehicle
VehicleType = v2_module.VehicleType
Customer = v2_module.Customer
RentalService = v2_module.RentalService
EquipmentType = v2_module.EquipmentType
ReservationStatus = v2_module.ReservationStatus

class TestV2Extended(unittest.TestCase):

    def setUp(self):
        RentalService.reset_instance()
        self.service = RentalService()
        self.vehicle = Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0)
        self.customer = self.service.register_customer("C1", "Alice", "alice@test.com", "DL-001")
        self.service.add_vehicle(self.vehicle)

    def test_equipment_add_on_cost(self):
        start = date.today()
        end = start + timedelta(days=2) # 2 days rental
        
        res = self.service.make_reservation(
            self.customer, self.vehicle, start, end, 
            equipments=[EquipmentType.CHILD_SEAT, EquipmentType.GPS]
        )
        self.assertEqual(150.0, res.total_cost)

    def test_late_return_penalty(self):
        start = date.today()
        end = start + timedelta(days=2)
        
        res = self.service.make_reservation(self.customer, self.vehicle, start, end)
        self.assertEqual(100.0, res.total_cost) # 2 days * 50
        
        self.service.pickup_vehicle(res)
        
        return_date = end + timedelta(days=2)
        self.service.return_vehicle(res, return_date=return_date)
        
        self.assertEqual(ReservationStatus.COMPLETED, res.status)
        self.assertEqual(300.0, res.total_cost)

if __name__ == '__main__':
    unittest.main()
