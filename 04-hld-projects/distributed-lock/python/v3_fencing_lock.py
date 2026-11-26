import unittest
import sys
import os

class FencingLock:
    def __init__(self):
        self.token = 0
        self.locked = False
    def acquire(self):
        if not self.locked:
            self.locked = True
            self.token += 1
            return self.token
        return 0
    def release(self):
        self.locked = False

class Resource:
    def __init__(self):
        self.last_token = 0
    def write(self, token, val):
        if token < self.last_token:
            return False # reject stale holder
        self.last_token = token
        return True

class TestFencingLock(unittest.TestCase):
    def test_stale_holder(self):
        l = FencingLock()
        r = Resource()
        t1 = l.acquire()
        l.release()
        t2 = l.acquire()
        self.assertTrue(r.write(t2, "val2"))
        self.assertFalse(r.write(t1, "val1")) # stale
    
    def test_2(self):
        l = FencingLock()
        self.assertTrue(l.acquire() > 0)
    def test_3(self):
        l = FencingLock()
        l.acquire()
        l.release()
        self.assertTrue(l.acquire() > 0)
    def test_4(self):
        l = FencingLock()
        self.assertTrue(l.acquire() > 0)
    def test_5(self):
        l = FencingLock()
        self.assertTrue(l.acquire() > 0)
    def test_6(self):
        l = FencingLock()
        self.assertTrue(l.acquire() > 0)

if __name__ == '__main__':
    unittest.main()
