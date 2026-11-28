import unittest
import sys
import os

# Mirror the v1 test's explicit path loading so flat imports inside the
# v2 modules resolve against the v2 files.
import importlib.util
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))
clock = import_module_from_path("clock", os.path.join(base_dir, "clock.py"))
exceptions = import_module_from_path("exceptions", os.path.join(base_dir, "exceptions.py"))
worker_id_pool = import_module_from_path("worker_id_pool", os.path.join(base_dir, "worker_id_pool.py"))
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


class TestSnowflakeGeneratorV2Parity(unittest.TestCase):
    """The v1 test scenarios re-run against v2 to lock in v1 behavior."""

    def test_next_id(self):
        clk = MockClock()
        generator = snowflake_generator.SnowflakeGenerator(1, 0, clk)

        self.assertEqual(generator.next_id(), (1000 << 22) | (1 << 12) | 0)
        self.assertEqual(generator.next_id(), (1000 << 22) | (1 << 12) | 1)

        clk.advance_millis(1)
        self.assertEqual(generator.next_id(), (1001 << 22) | (1 << 12) | 0)

    def test_sequence_rollover(self):
        class SequenceRolloverClock(clock.Clock):
            def __init__(self):
                self.calls = 0

            def current_time_millis(self) -> int:
                if self.calls <= 4096:
                    self.calls += 1
                    return 1000
                return 1001

        generator = snowflake_generator.SnowflakeGenerator(1, 0, SequenceRolloverClock())
        for i in range(4096):
            self.assertEqual(generator.next_id(), (1000 << 22) | (1 << 12) | i)
        self.assertEqual(generator.next_id(), (1001 << 22) | (1 << 12) | 0)

    def test_clock_moved_backwards_throws_by_default(self):
        clk = MockClock()
        generator = snowflake_generator.SnowflakeGenerator(1, 0, clk)
        generator.next_id()  # time = 1000
        clk.set_time(999)
        with self.assertRaises(exceptions.ClockMovedBackwardsException):
            generator.next_id()


class TestSnowflakeGeneratorV2(unittest.TestCase):
    """Tests for the three named v2 improvements."""

    # --- Improvement #1: configurable backwards-clock policy ---

    def test_wait_policy_tolerates_small_backwards_jump(self):
        class RecoveringClock(clock.Clock):
            def __init__(self):
                self.reads = 0

            def current_time_millis(self) -> int:
                self.reads += 1
                if self.reads == 1:
                    return 1000
                if self.reads <= 6:
                    return 995 + (self.reads - 2)  # 995..999, then 1000
                return 1000

        generator = snowflake_generator.SnowflakeGenerator(
            1, 0, RecoveringClock(),
            backwards_policy=snowflake_generator.BackwardsClockPolicy.WAIT,
            max_wait_millis=5)

        self.assertEqual(generator.next_id(), (1000 << 22) | (1 << 12) | 0)
        # Clock dipped to 995, then recovered; the generator blocked until
        # it caught up to 1000 and continued the same-millisecond sequence.
        self.assertEqual(generator.next_id(), (1000 << 22) | (1 << 12) | 1)

    def test_wait_policy_rejects_jump_beyond_tolerance(self):
        clk = MockClock()
        generator = snowflake_generator.SnowflakeGenerator(
            1, 0, clk,
            backwards_policy=snowflake_generator.BackwardsClockPolicy.WAIT,
            max_wait_millis=10)
        generator.next_id()  # time = 1000
        clk.set_time(900)  # 100ms backwards, beyond the 10ms tolerance
        with self.assertRaises(exceptions.ClockMovedBackwardsException):
            generator.next_id()

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            snowflake_generator.SnowflakeGenerator(1, 0, MockClock(), backwards_policy="panic")

    # --- Improvement #3: timestamp-overflow guard ---

    def test_overflow_guard_raises_beyond_41_bits(self):
        clk = MockClock()
        generator = snowflake_generator.SnowflakeGenerator(1, 0, clk)
        clk.set_time((1 << 41))  # one millisecond past the 41-bit delta field
        with self.assertRaises(exceptions.TimestampOverflowException):
            generator.next_id()

    def test_overflow_guard_allows_max_delta(self):
        clk = MockClock()
        generator = snowflake_generator.SnowflakeGenerator(1, 0, clk)
        clk.set_time((1 << 41) - 1)
        expected = (((1 << 41) - 1) << 22) | (1 << 12) | 0
        self.assertEqual(generator.next_id(), expected)

    # --- Improvement #2: dynamic worker-ID leasing ---

    def test_pool_acquire_is_collision_proof(self):
        pool = worker_id_pool.WorkerIdPool()
        first = pool.acquire()
        second = pool.acquire()
        self.assertNotEqual(first, second)
        self.assertTrue(pool.is_leased(first))
        self.assertTrue(pool.is_leased(second))

    def test_pool_acquires_lowest_free_id(self):
        pool = worker_id_pool.WorkerIdPool()
        self.assertEqual(pool.acquire(), 0)
        self.assertEqual(pool.acquire(), 1)

    def test_pool_release_returns_id_to_pool(self):
        pool = worker_id_pool.WorkerIdPool()
        worker_id = pool.acquire()
        pool.release(worker_id)
        self.assertFalse(pool.is_leased(worker_id))
        # A replacement node picks the same freed ID up again.
        self.assertEqual(pool.acquire(), worker_id)

    def test_pool_exhaustion_is_loud(self):
        pool = worker_id_pool.WorkerIdPool(max_worker_id=1)
        pool.acquire()
        pool.acquire()
        self.assertEqual(pool.leased_count(), 2)
        with self.assertRaises(exceptions.WorkerIdPoolExhaustedError):
            pool.acquire()

    def test_pool_release_unleased_id_raises(self):
        pool = worker_id_pool.WorkerIdPool()
        with self.assertRaises(ValueError):
            pool.release(7)


if __name__ == '__main__':
    unittest.main()
