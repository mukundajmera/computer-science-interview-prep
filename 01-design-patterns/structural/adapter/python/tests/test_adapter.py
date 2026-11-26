"""
Tests for Adapter Pattern implementations
"""
import unittest
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-pythonic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-advanced'))


class TestV1BasicAdapter(unittest.TestCase):
    """Tests for V1 Basic Media Player Adapter"""
    
    def test_vlc_adapter_implements_interface(self):
        """VLC Adapter should implement MediaPlayer interface"""
        from adapter_demo import VLCPlayer, VLCPlayerAdapter, MediaPlayer
        
        vlc = VLCPlayer()
        adapter = VLCPlayerAdapter(vlc)
        
        # Should implement MediaPlayer
        self.assertTrue(isinstance(adapter, MediaPlayer))
        self.assertEqual(adapter.get_player_type(), "VLC")
    
    def test_mp4_adapter_translates_calls(self):
        """MP4 Adapter should translate method calls correctly"""
        from adapter_demo import MP4PlayerAdapter
        
        adapter = MP4PlayerAdapter()
        
        # Should not raise
        adapter.play("video.mp4")
        adapter.stop()
        self.assertEqual(adapter.get_player_type(), "MP4")
    
    def test_client_works_with_any_adapter(self):
        """Client should work with any adapter"""
        from adapter_demo import AudioPlayerClient, VLCPlayerAdapter, MP4PlayerAdapter
        
        client = AudioPlayerClient()
        
        # Test with VLC
        client.set_player(VLCPlayerAdapter())
        client.play_file("movie.vlc")  # Should not raise
        
        # Test with MP4
        client.set_player(MP4PlayerAdapter())
        client.play_file("video.mp4")  # Should not raise


class TestV2PythonicAdapter(unittest.TestCase):
    """Tests for V2 Pythonic Payment Adapter"""
    
    def test_stripe_adapter_processes_payment(self):
        """Stripe adapter should process payments"""
        from payment_adapter import StripeAdapter, StripeAPI
        
        adapter = StripeAdapter(StripeAPI())
        card = {"number": "4111111111111111", "expiry": "12/25", "cvv": "123"}
        
        result = adapter.process_payment(99.99, "USD", card)
        
        self.assertTrue(result)
        self.assertEqual(adapter.get_provider_name(), "Stripe")
    
    def test_paypal_adapter_processes_payment(self):
        """PayPal adapter should process payments"""
        from payment_adapter import PayPalAdapter, PayPalSDK
        
        adapter = PayPalAdapter(PayPalSDK())
        
        result = adapter.process_payment(49.99, "USD", {})
        
        self.assertTrue(result)
        self.assertEqual(adapter.get_provider_name(), "PayPal")
    
    def test_factory_creates_correct_adapter(self):
        """Factory should create correct adapter type"""
        from payment_adapter import create_payment_adapter, StripeAPI, PayPalSDK
        
        stripe = create_payment_adapter(StripeAPI(), "stripe")
        paypal = create_payment_adapter(PayPalSDK(), "paypal")
        
        self.assertEqual(stripe.get_provider_name(), "Stripe")
        self.assertEqual(paypal.get_provider_name(), "PayPal")
    
    def test_factory_raises_for_unknown_type(self):
        """Factory should raise for unknown adapter type"""
        from payment_adapter import create_payment_adapter
        
        with self.assertRaises(ValueError):
            create_payment_adapter(None, "unknown")


class TestV3AdvancedAdapter(unittest.TestCase):
    """Tests for V3 Advanced Two-Way Adapter"""
    
    def test_xml_to_json_conversion(self):
        """Two-way adapter should convert XML to JSON"""
        from two_way_adapter import LegacyXMLDatabase, TwoWayDataAdapter
        
        xml_db = LegacyXMLDatabase()
        adapter = TwoWayDataAdapter(xml_source=xml_db)
        
        json_data = adapter.fetch_as_json("user_1")
        
        self.assertEqual(json_data["id"], 1)
        self.assertEqual(json_data["name"], "Alice")
    
    def test_json_to_xml_conversion(self):
        """Two-way adapter should convert JSON to XML"""
        from two_way_adapter import ModernJSONAPI, TwoWayDataAdapter
        
        json_api = ModernJSONAPI()
        adapter = TwoWayDataAdapter(json_source=json_api)
        
        xml_data = adapter.fetch_as_xml("product_1")
        
        self.assertIn("<id>1</id>", xml_data)
        self.assertIn("<name>Laptop</name>", xml_data)
    
    def test_context_manager(self):
        """Adapter should work as context manager"""
        from two_way_adapter import LegacyXMLDatabase, TwoWayDataAdapter
        
        xml_db = LegacyXMLDatabase()
        
        with TwoWayDataAdapter(xml_source=xml_db) as adapter:
            adapter.fetch_as_json("user_1")
            adapter.fetch_as_json("user_2")
            
            self.assertEqual(adapter.transaction_count, 2)
    
    def test_save_json_to_xml_system(self):
        """Two-way adapter should save JSON to XML system"""
        from two_way_adapter import LegacyXMLDatabase, TwoWayDataAdapter
        
        xml_db = LegacyXMLDatabase()
        adapter = TwoWayDataAdapter(xml_source=xml_db)
        
        adapter.save_from_json({"id": 99, "name": "Test", "email": "test@test.com"})
        
        saved = xml_db.fetch_as_xml("user_99")
        self.assertIn("<id>99</id>", saved)
    
    def test_empty_data_handling(self):
        """Adapter should handle empty/missing data"""
        from two_way_adapter import LegacyXMLDatabase, TwoWayDataAdapter
        
        xml_db = LegacyXMLDatabase()
        adapter = TwoWayDataAdapter(xml_source=xml_db)
        
        result = adapter.fetch_as_json("nonexistent")
        
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
