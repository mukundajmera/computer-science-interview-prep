import uuid
import unittest
import sys
import os

class UUIDGen:
    def next_id(self):
        return uuid.uuid4()

class TestUUID(unittest.TestCase):
    def test_1(self):
        self.assertIsNotNone(UUIDGen().next_id())
    def test_2(self):
        self.assertNotEqual(UUIDGen().next_id(), UUIDGen().next_id())
    def test_3(self):
        self.assertIsNotNone(UUIDGen().next_id())
    def test_4(self):
        self.assertIsNotNone(UUIDGen().next_id())
    def test_5(self):
        self.assertIsNotNone(UUIDGen().next_id())
    def test_6(self):
        self.assertIsNotNone(UUIDGen().next_id())

if __name__ == '__main__':
    unittest.main()
