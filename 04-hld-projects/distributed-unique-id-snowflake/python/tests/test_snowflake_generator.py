import unittest
import sys
import os

# Adjust path to import v1-basic module
import importlib.util
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
clock = import_module_from_path("clock", os.path.join(base_dir, "clock.py"))
exceptions = import_module_from_path("exceptions", os.path.join(base_dir, "exceptions.py"))
snowflake_generator = import_module_from_path("snowflake_generator", os.path.join(base_dir, "snowflake_generator.py"))

class MockClock(clock.Clock):
    def __init__(self):
        self.time = 1000

    def current_time_millis(self) -> int:
        return self.time

    def advance_millis(self, millis: int):
        self.time += millis
        
    def set_time(self, time: int):
        self.time = time

class TestSnowflakeGenerator(unittest.TestCase):

    def test_next_id(self):
        clk = MockClock()
        epoch = 0
        generator = snowflake_generator.SnowflakeGenerator(1, epoch, clk)

        id1 = generator.next_id()
        id2 = generator.next_id()

        self.assertEqual(id1, (1000 << 22) | (1 << 12) | 0)
        self.assertEqual(id2, (1000 << 22) | (1 << 12) | 1)

        clk.advance_millis(1)
        id3 = generator.next_id()
        self.assertEqual(id3, (1001 << 22) | (1 << 12) | 0)

    def test_sequence_rollover(self):
        class SequenceRolloverClock(clock.Clock):
            def __init__(self):
                self.calls = 0
                
            def current_time_millis(self) -> int:
                if self.calls <= 4096:
                    self.calls += 1
                    return 1000
                return 1001

        clk = SequenceRolloverClock()
        epoch = 0
        generator = snowflake_generator.SnowflakeGenerator(1, epoch, clk)

        for i in range(4096):
            id_val = generator.next_id()
            self.assertEqual(id_val, (1000 << 22) | (1 << 12) | i)

        # 4097th call
        id_val = generator.next_id()
        self.assertEqual(id_val, (1001 << 22) | (1 << 12) | 0)

    def test_clock_moved_backwards(self):
        clk = MockClock()
        epoch = 0
        generator = snowflake_generator.SnowflakeGenerator(1, epoch, clk)

        generator.next_id()  # time = 1000
        clk.set_time(999)  # clock moved backwards

        with self.assertRaises(exceptions.ClockMovedBackwardsException):
            generator.next_id()

if __name__ == '__main__':
    unittest.main()
