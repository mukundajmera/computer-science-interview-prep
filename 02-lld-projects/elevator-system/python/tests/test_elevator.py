"""
Elevator System Tests
"""
import sys
import os
import unittest
import importlib.util

# Helper function to dynamically load modules from hyphenated directories
def load_module(version_dir, module_name):
    # Load module dynamically to test versions with hyphens in directory names
    file_path = os.path.join(os.path.dirname(__file__), '..', version_dir, f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class TestElevatorBase(unittest.TestCase):
    version_dir = ""

    def setUp(self):
        # We don't want the base class to run tests itself if version_dir is empty
        if not self.version_dir:
            self.skipTest("Base class")
            return
            
        self.module = load_module(self.version_dir, 'elevator')
        self.Elevator = self.module.Elevator
        self.Direction = self.module.Direction
        
        # v1 and v3 initialize elevators with ID, while others might differ. 
        # We will use id=0.
        self.elevator = self.Elevator(id=0, capacity=10)
    
    def test_initial_state(self):
        self.assertEqual(0, self.elevator.current_floor)
        self.assertEqual(self.Direction.IDLE, self.elevator.direction)
    
    def test_add_request(self):
        self.elevator.add_request(5)
        self.assertIn(5, self.elevator._requests)
    
    def test_move_up(self):
        self.elevator.add_request(3)
        self.elevator.move()
        # V2 uses State Pattern, so first it changes to MovingState and starts to move
        # Let's ensure current_floor changes if we step appropriately
        
        # In v2, first move processes the state change
        if self.version_dir == "v2-extended":
            self.assertEqual(1, self.elevator.current_floor)
        else:
            self.assertEqual(1, self.elevator.current_floor)
        # Depending on SCAN or other algorithm, direction could be UP
        self.assertEqual(self.Direction.UP, self.elevator.direction)
    
    def test_reach_destination(self):
        self.elevator.add_request(1)
        self.elevator.move()
        self.assertEqual(1, self.elevator.current_floor)
        
        if self.version_dir == "v2-extended":
            # For V2, the current floor is reached and we transition to StoppedState
            # Let's call move again if we want to simulate the stop being processed,
            # wait, in V2, if current_floor == next_floor, it sets StoppedState,
            # but hasn't opened doors and removed request yet. 
            self.elevator.move()
        self.assertNotIn(1, self.elevator._requests)

class TestElevatorV1(TestElevatorBase):
    version_dir = "v1-basic"

class TestElevatorV2(TestElevatorBase):
    version_dir = "v2-extended"

class TestElevatorV3(TestElevatorBase):
    version_dir = "v3-optimized"

if __name__ == "__main__":
    unittest.main(verbosity=2)
