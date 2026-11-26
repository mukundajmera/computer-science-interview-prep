import sys
import unittest
import importlib.util
import os

def load_v3():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v3-optimized"))
    sys.path.insert(0, base_dir)
    
    spec1 = importlib.util.spec_from_file_location("notification_v3", os.path.join(base_dir, "notification.py"))
    notif = importlib.util.module_from_spec(spec1)
    sys.modules["notification"] = notif
    spec1.loader.exec_module(notif)

    spec2 = importlib.util.spec_from_file_location("notification_service_v3", os.path.join(base_dir, "notification_service.py"))
    svc = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(svc)
    return notif, svc

class TestNotificationServiceAllVersions(unittest.TestCase):
    def setUp(self):
        self.notification, self.notification_service = load_v3()
        
    def test_idempotency_and_preferences(self):
        dispatcher = self.notification.Dispatcher(rate_limit=100, max_retries=1)
        service = self.notification_service.NotificationService(dispatcher, capacity=5, max_retries=1)
        
        service.unsubscribe("u3")
        state = service.submit_intent("PROMO", "u1", "EMAIL", "Hello")
        self.assertEqual(state.name, "PENDING")
        
        state2 = service.submit_intent("PROMO", "u1", "EMAIL", "Hello")
        self.assertEqual(state2.name, "CONFLICT")
        
        for i in range(4):
            service.submit_intent("PROMO", f"u{i+10}", "EMAIL", "Hello")
            
        state_overflow = service.submit_intent("PROMO", "u100", "EMAIL", "Hello")
        self.assertEqual(state_overflow.name, "FAILED")
        
    def test_delivery_state_transitions(self):
        dispatcher = self.notification.Dispatcher(rate_limit=100, max_retries=1)
        service = self.notification_service.NotificationService(dispatcher, capacity=10, max_retries=1)
        
        class MockFailingChannel(self.notification.Channel):
            def send(self, notif):
                return False
                
        class MockSuccessChannel(self.notification.Channel):
            def send(self, notif):
                return True
                
        service.wrap_channel("EMAIL", MockFailingChannel())
        service.wrap_channel("SMS", MockSuccessChannel())
        
        service.submit_intent("ALERT", "u1", "EMAIL", "Hello")
        service.submit_intent("ALERT", "u2", "SMS", "Hello")
        
        self.assertEqual(service.get_intent_state("ALERT:u1:EMAIL").name, "PENDING")
        self.assertEqual(service.get_intent_state("ALERT:u2:SMS").name, "PENDING")
        
        dispatcher.process_one() # EMAIL attempt 1 (fails)
        dispatcher.process_one() # SMS attempt 1 (succeeds)
        
        self.assertEqual(service.get_intent_state("ALERT:u2:SMS").name, "COMPLETED")
        self.assertEqual(service.get_intent_state("ALERT:u1:EMAIL").name, "IN_PROGRESS") 
        
        import unittest.mock, time
        with unittest.mock.patch('time.time', return_value=time.time() + 10):
            dispatcher.process_one() # EMAIL attempt 2 (fails) -> Max retries
            
        self.assertEqual(service.get_intent_state("ALERT:u1:EMAIL").name, "FAILED")

if __name__ == '__main__':
    unittest.main()
