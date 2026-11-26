import os
import sys
import time
import threading
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

import log_level
import logger_factory
import appenders

sys.path.pop(0)

@pytest.fixture(autouse=True)
def setup_teardown():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
    import logger_factory as lf
    lf.LoggerFactory.reset()
    yield
    if lf.LoggerFactory._instance is not None:
        lf.LoggerFactory._instance.shutdown()
    sys.path.pop(0)

def test_log_level_filtering():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
    import log_level as ll
    import logger_factory as lf
    import appenders as ap

    factory = lf.LoggerFactory.get_instance()
    root = factory.get_logger("root")
    
    appender = ap.InMemoryAppender("Memory")
    root.appenders.clear()
    root.add_appender(appender)
    
    root.set_level(ll.LogLevel.INFO)
    
    root.debug("Debug msg")
    root.info("Info msg")
    root.error("Error msg")
    
    time.sleep(0.1)
    
    logs = appender.get_logs()
    assert len(logs) == 2
    assert logs[0].level.value == ll.LogLevel.INFO.value
    assert logs[1].level.value == ll.LogLevel.ERROR.value
    sys.path.pop(0)

def test_multi_threaded_async_log_flushing():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
    import log_level as ll
    import logger_factory as lf
    import appenders as ap

    factory = lf.LoggerFactory.get_instance()
    root = factory.get_logger("root")
    
    root.appenders.clear()
    
    appender = ap.InMemoryAppender("Memory")
    root.add_appender(appender)
    root.set_level(ll.LogLevel.INFO)
    
    thread_count = 10
    logs_per_thread = 100
    
    def log_task(thread_id):
        for j in range(logs_per_thread):
            root.info(f"Thread {thread_id} log {j}")
            
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=log_task, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    time.sleep(0.5)
    
    logs = appender.get_logs()
    assert len(logs) == thread_count * logs_per_thread
    sys.path.pop(0)
