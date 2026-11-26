"""
Unit tests for LinkedIn Connection System
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))

from user import User
from network_service import NetworkService


class TestUser(unittest.TestCase):
    
    def test_user_creation(self):
        user = User("U001", "Alice", "alice@email.com")
        self.assertEqual("U001", user.user_id)
        self.assertEqual("Alice", user.name)
    
    def test_add_connection(self):
        alice = User("U001", "Alice", "alice@email.com")
        bob = User("U002", "Bob", "bob@email.com")
        
        alice.add_connection(bob)
        bob.add_connection(alice)
        
        self.assertTrue(alice.is_connected_to(bob))
        self.assertTrue(bob.is_connected_to(alice))
    
    def test_mutual_connections(self):
        alice = User("U001", "Alice", "alice@email.com")
        bob = User("U002", "Bob", "bob@email.com")
        charlie = User("U003", "Charlie", "charlie@email.com")
        
        alice.add_connection(bob)
        alice.add_connection(charlie)
        bob.add_connection(alice)
        bob.add_connection(charlie)
        charlie.add_connection(alice)
        charlie.add_connection(bob)
        
        mutual = alice.get_mutual_connections(bob)
        self.assertEqual(1, len(mutual))
        self.assertIn(charlie, mutual)


class TestNetworkService(unittest.TestCase):
    
    def setUp(self):
        NetworkService.reset_instance()
    
    def tearDown(self):
        NetworkService.reset_instance()
    
    def test_singleton(self):
        ns1 = NetworkService.get_instance()
        ns2 = NetworkService.get_instance()
        self.assertIs(ns1, ns2)
    
    def test_register_user(self):
        network = NetworkService.get_instance()
        alice = User("U001", "Alice", "alice@email.com")
        
        self.assertTrue(network.register_user(alice))
        self.assertEqual(alice, network.get_user("U001"))
    
    def test_connection_request(self):
        network = NetworkService.get_instance()
        alice = User("U001", "Alice", "alice@email.com")
        bob = User("U002", "Bob", "bob@email.com")
        
        network.register_user(alice)
        network.register_user(bob)
        
        request = network.send_connection_request("U001", "U002")
        self.assertIsNotNone(request)
        self.assertTrue(request.is_pending())
        
        network.accept_request(request.request_id)
        self.assertTrue(network.are_connected("U001", "U002"))
    
    def test_connection_degree(self):
        network = NetworkService.get_instance()
        a = User("A", "A", "a@email.com")
        b = User("B", "B", "b@email.com")
        c = User("C", "C", "c@email.com")
        d = User("D", "D", "d@email.com")
        
        for u in [a, b, c, d]:
            network.register_user(u)
        
        r1 = network.send_connection_request("A", "B")
        r2 = network.send_connection_request("B", "C")
        r3 = network.send_connection_request("C", "D")
        
        for r in [r1, r2, r3]:
            network.accept_request(r.request_id)
        
        self.assertEqual(1, network.get_connection_degree("A", "B"))
        self.assertEqual(2, network.get_connection_degree("A", "C"))
        self.assertEqual(3, network.get_connection_degree("A", "D"))
    
    def test_endorsement(self):
        network = NetworkService.get_instance()
        alice = User("U001", "Alice", "alice@email.com")
        bob = User("U002", "Bob", "bob@email.com")
        
        alice.add_skill("Java")
        
        network.register_user(alice)
        network.register_user(bob)
        
        req = network.send_connection_request("U001", "U002")
        network.accept_request(req.request_id)
        
        self.assertTrue(network.endorse_skill("U002", "U001", "Java"))
        
        skill = alice.get_skill("Java")
        self.assertEqual(1, skill.get_endorsement_count())


if __name__ == '__main__':
    unittest.main()
