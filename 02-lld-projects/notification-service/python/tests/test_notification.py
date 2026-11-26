import pytest
import importlib.util
import sys
import time
import os

def load_module(version):
    module_name = f"{version}_notification"
    file_path = f"02-lld-projects/notification-service/python/{version}/notification.py"
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_service_module(version):
    base_dir = os.path.abspath("02-lld-projects/notification-service/python")
    v_dir = os.path.join(base_dir, version)
    sys.path.insert(0, v_dir)
    try:
        if "notification_service" in sys.modules:
            del sys.modules["notification_service"]
        if "notification" in sys.modules:
            del sys.modules["notification"]
        import notification
        import notification_service
        return notification_service
    finally:
        sys.path.pop(0)

def test_v1_dispatch():
    mod = load_module("v1-basic")
    dispatcher = mod.Dispatcher()
    n = mod.Notification("u1", "hello", "EMAIL")
    assert dispatcher.dispatch(n) == True

def test_v1_notification_service():
    mod = load_module("v1-basic")
    notification_service = load_service_module("v1-basic")
    
    dispatcher = mod.Dispatcher()
    service = notification_service.NotificationService(dispatcher, capacity=2, max_retries=1)
    
    # Idempotency
    assert service.submit_intent("PROMO", "u1", "EMAIL", "msg1") == notification_service.IntentState.PENDING
    assert service.submit_intent("PROMO", "u1", "EMAIL", "msg1") == notification_service.IntentState.CONFLICT
    
    # Unsubscribe
    service.unsubscribe("u2")
    assert service.submit_intent("PROMO", "u2", "EMAIL", "msg2") == notification_service.IntentState.FAILED
    
    # Overflow
    service_small = notification_service.NotificationService(dispatcher, capacity=0, max_retries=0)
    assert service_small.submit_intent("PROMO", "u3", "EMAIL", "msg") == notification_service.IntentState.FAILED
    
    # Fake hanging provider
    class HangingChannel(mod.Channel):
        def send(self, notification):
            time.sleep(5)
            return False
            
    hanging_dispatcher = mod.Dispatcher()
    hanging_dispatcher.channels["HANG"] = HangingChannel()
    
    service_hanging = notification_service.NotificationService(hanging_dispatcher, capacity=10, max_retries=0)
    start_time = time.time()
    assert service_hanging.submit_intent("ALERT", "u4", "HANG", "msg") == notification_service.IntentState.PENDING
    duration = time.time() - start_time
    assert duration < 1.0, "Main thread should not block"

def test_v2_priority():
    mod = load_module("v2-extended")
    dispatcher = mod.Dispatcher()
    
    n1 = mod.Notification("u1", "low", "EMAIL", priority=2)
    n2 = mod.Notification("u2", "high", "EMAIL", priority=1)
    
    dispatcher.enqueue(n1)
    dispatcher.enqueue(n2)
    
    assert dispatcher.queue.queue[0].user_id == "u2"

def test_v2_rate_limit():
    mod = load_module("v2-extended")
    dispatcher = mod.Dispatcher(rate_limit=1)
    
    n1 = mod.Notification("u1", "msg1", "EMAIL")
    n2 = mod.Notification("u2", "msg2", "EMAIL")
    
    dispatcher.enqueue(n1)
    dispatcher.enqueue(n2)
    
    assert dispatcher.process_one() == True 
    assert dispatcher.process_one() == False 

def test_v2_notification_service():
    mod = load_module("v2-extended")
    notification_service = load_service_module("v2-extended")
    
    base_dir = os.path.abspath("02-lld-projects/notification-service/python")
    v2_dir = os.path.join(base_dir, "v2-extended")
    sys.path.insert(0, v2_dir)
    
    try:
        dispatcher = mod.Dispatcher()
        service = notification_service.NotificationService(dispatcher, capacity=2, max_retries=1)
        
        # Idempotency
        assert service.submit_intent("PROMO", "u1", "EMAIL", "msg1") == notification_service.IntentState.PENDING
        assert service.submit_intent("PROMO", "u1", "EMAIL", "msg1") == notification_service.IntentState.CONFLICT
        
        # Unsubscribe
        service.unsubscribe("u2")
        assert service.submit_intent("PROMO", "u2", "EMAIL", "msg2") == notification_service.IntentState.FAILED
        
        # Overflow
        service_small = notification_service.NotificationService(dispatcher, capacity=0, max_retries=0)
        assert service_small.submit_intent("PROMO", "u3", "EMAIL", "msg") == notification_service.IntentState.FAILED
        
        # Fake hanging provider
        class HangingChannel(mod.Channel):
            def send(self, notification):
                time.sleep(5)
                return False
                
        hanging_dispatcher = mod.Dispatcher()
        service_hanging = notification_service.NotificationService(hanging_dispatcher, capacity=10, max_retries=0)
        service_hanging.wrap_channel("HANG", HangingChannel())
        
        start_time = time.time()
        assert service_hanging.submit_intent("ALERT", "u4", "HANG", "msg") == notification_service.IntentState.PENDING
        duration = time.time() - start_time
        assert duration < 1.0, "Main thread should not block"
    finally:
        sys.path.pop(0)

def test_v3_retry():
    mod = load_module("v3-optimized")
    dispatcher = mod.Dispatcher(max_retries=3)
    
    class MockFailOnceEmailChannel(mod.Channel):
        def send(self, notification):
            if notification.attempts == 0:
                return False
            return True
            
    dispatcher.channels["EMAIL"] = MockFailOnceEmailChannel()
    n1 = mod.Notification("u1", "msg1", "EMAIL")
    dispatcher.enqueue(n1)
    
    assert dispatcher.process_one() == False
    assert n1.attempts == 1
    
    # Needs to wait for exponential backoff (base * 2^1 = 2 seconds)
    # We can fake the time to pass it quickly
    import unittest.mock
    with unittest.mock.patch('time.time', return_value=n1.next_retry_time + 1):
        assert dispatcher.process_one() == True

def test_v3_preferences_and_channels():
    mod = load_module("v3-optimized")
    dispatcher = mod.Dispatcher(max_retries=1)
    
    dispatcher.user_preferences.set_preference("u1", "MARKETING", ["SMS", "PUSH"])
    dispatcher.user_preferences.set_preference("u2", "ALERT", ["SLACK"])
    
    assert dispatcher.dispatch_based_on_preference("u1", "sale", "MARKETING") == True
    assert dispatcher.dispatch_based_on_preference("u2", "error", "ALERT") == True
    
    # Check queue sizes and channel types
    notifs = []
    while not dispatcher.queue.empty():
        notifs.append(dispatcher.queue.get())
        
    channels = set(n.channel_type for n in notifs)
    assert channels == {"SMS", "PUSH", "SLACK"}
