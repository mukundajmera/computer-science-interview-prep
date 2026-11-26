import unittest
import sys
import os

# sys.path config if needed
class TicketServer:
    def __init__(self):
        self.val = 0
    def next_id(self):
        self.val += 1
        return self.val

class TestTicket(unittest.TestCase):
    def test_1(self):
        t = TicketServer()
        self.assertEqual(t.next_id(), 1)
    def test_2(self):
        t = TicketServer()
        t.next_id()
        self.assertEqual(t.next_id(), 2)
    def test_3(self):
        t = TicketServer()
        self.assertTrue(t.next_id() > 0)
    def test_4(self):
        t = TicketServer()
        self.assertEqual(t.next_id(), 1)
    def test_5(self):
        t = TicketServer()
        self.assertEqual(t.next_id(), 1)
    def test_6(self):
        t = TicketServer()
        self.assertEqual(t.next_id(), 1)

if __name__ == '__main__':
    unittest.main()
