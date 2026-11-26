import unittest
import sys
import os

class LockV1:
    def __init__(self):
        self.locked = False
    def acquire(self):
        if not self.locked:
            self.locked = True
            return True
        return False
    def release(self):
        self.locked = False

class TestLockV1(unittest.TestCase):
    def test_1(self):
        l = LockV1()
        self.assertTrue(l.acquire())
    def test_2(self):
        l = LockV1()
        l.acquire()
        self.assertFalse(l.acquire())
    def test_3(self):
        l = LockV1()
        l.acquire()
        l.release()
        self.assertTrue(l.acquire())
    def test_4(self):
        l = LockV1()
        self.assertTrue(l.acquire())
    def test_5(self):
        l = LockV1()
        self.assertTrue(l.acquire())
    def test_6(self):
        l = LockV1()
        self.assertTrue(l.acquire())

if __name__ == '__main__':
    unittest.main()
