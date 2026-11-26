import sys
import os
import unittest
import threading
import random
import time

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib.util

spec = importlib.util.spec_from_file_location('elevator', os.path.join(os.path.dirname(__file__), '..', 'v3-optimized', 'elevator.py'))
elevator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elevator_module)
ElevatorSystem = elevator_module.ElevatorSystem
Direction = elevator_module.Direction

class TestConcurrency(unittest.TestCase):
    def setUp(self):
        # Reset the singleton for clean tests
        ElevatorSystem._instance = None
        self.system = ElevatorSystem(num_elevators=4, num_floors=20)
        
    def test_concurrent_requests(self):
        """Stress test with 8 worker threads asserting absence of race conditions"""
        num_threads = 8
        requests_per_thread = 50
        threads = []
        
        def worker(thread_id):
            # Each thread makes requests to random floors
            random.seed(thread_id)
            for _ in range(requests_per_thread):
                floor = random.randint(0, 20)
                direction = random.choice([Direction.UP, Direction.DOWN])
                self.system.request_elevator(floor, direction)
                
                # Small sleep to simulate realistic delay and increase race condition likelihood without locks
                time.sleep(0.001)

        # Start all threads
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
            
        # Also simulate the system stepping while requests are coming in
        def system_runner():
            for _ in range(requests_per_thread * 2):
                self.system.step()
                time.sleep(0.002)
                
        runner_thread = threading.Thread(target=system_runner)
        runner_thread.start()

        # Wait for all request threads to finish
        for t in threads:
            t.join()
            
        # Wait for the runner thread
        runner_thread.join()
        
        # Verify all elevators are in a valid state
        for elevator in self.system.elevators.values():
            with elevator.lock:
                # The requests list should be sorted
                sorted_requests = sorted(elevator._requests)
                self.assertEqual(elevator._requests, sorted_requests, 
                                 f"Requests not sorted in elevator {elevator.id}: {elevator._requests}")
                
                # No duplicates allowed
                self.assertEqual(len(elevator._requests), len(set(elevator._requests)),
                                 f"Duplicate requests found in elevator {elevator.id}: {elevator._requests}")
                
                # Ensure current_floor is within valid range (we allowed up to 20 but could go beyond if bugs)
                self.assertTrue(0 <= elevator.current_floor <= 20, 
                                f"Elevator {elevator.id} went out of bounds: {elevator.current_floor}")

if __name__ == "__main__":
    unittest.main()
