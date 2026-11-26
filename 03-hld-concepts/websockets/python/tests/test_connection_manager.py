import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from connection_manager import ConnectionManager


class TestConnectionManager(unittest.TestCase):
    def test_connect_adds_client(self):
        manager = ConnectionManager()
        manager.connect("room", "u1")
        self.assertEqual(manager.broadcast_targets("room"), ["u1"])

    def test_disconnect_removes_client(self):
        manager = ConnectionManager()
        manager.connect("room", "u1")
        manager.disconnect("room", "u1")
        self.assertEqual(manager.broadcast_targets("room"), [])

    def test_connect_is_idempotent_for_same_client(self):
        manager = ConnectionManager()
        manager.connect("room", "u1")
        manager.connect("room", "u1")
        self.assertEqual(manager.broadcast_targets("room"), ["u1"])

    def test_broadcast_targets_for_missing_room_do_not_create_members(self):
        manager = ConnectionManager()
        self.assertEqual(manager.broadcast_targets("missing"), [])
        self.assertEqual(manager.broadcast_targets("missing"), [])


if __name__ == '__main__':
    unittest.main()
