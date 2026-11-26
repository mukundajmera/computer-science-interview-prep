import time
import unittest
import sys
import os

class Snowflake:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def next_id(self):
        timestamp = int(time.time() * 1000)
        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards")
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                while timestamp <= self.last_timestamp:
                    timestamp = int(time.time() * 1000)
        else:
            self.sequence = 0
        self.last_timestamp = timestamp
        return (timestamp << 22) | (self.worker_id << 12) | self.sequence

class TestSnowflake(unittest.TestCase):
    def test_monotonic(self):
        s = Snowflake(1)
        ids = [s.next_id() for _ in range(10)]
        for i in range(1, len(ids)):
            self.assertTrue(ids[i] > ids[i-1])

    def test_clock_regression(self):
        s = Snowflake(1)
        s.last_timestamp = int(time.time() * 1000) + 10000
        with self.assertRaises(Exception):
            s.next_id()

    def test_3(self):
        s = Snowflake(1)
        self.assertTrue(s.next_id() > 0)
    
    def test_4(self):
        s = Snowflake(2)
        self.assertTrue(s.next_id() > 0)

    def test_5(self):
        s = Snowflake(3)
        self.assertTrue(s.next_id() > 0)
        
    def test_6(self):
        s = Snowflake(4)
        self.assertTrue(s.next_id() > 0)

if __name__ == '__main__':
    unittest.main()
