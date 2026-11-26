import unittest
import time
import sys
import os

class LockV2:
    def __init__(self):
        self.locked = False
        self.expires = 0
    def acquire(self):
        now = time.time()
        if not self.locked or now > self.expires:
            self.locked = True
            self.expires = now + 1
            return True
        return False
    def release(self):
        self.locked = False

class TestLockV2(unittest.TestCase):
    def test_1(self):
        l = LockV2()
        self.assertTrue(l.acquire())
    def test_2(self):
        l = LockV2()
        l.acquire()
        self.assertFalse(l.acquire())
    def test_3(self):
        l = LockV2()
        l.acquire()
        l.release()
        self.assertTrue(l.acquire())
    def test_4(self):
        l = LockV2()
        self.assertTrue(l.acquire())
    def test_5(self):
        l = LockV2()
        self.assertTrue(l.acquire())
    def test_6(self):
        l = LockV2()
        self.assertTrue(l.acquire())

if __name__ == '__main__':
    unittest.main()
