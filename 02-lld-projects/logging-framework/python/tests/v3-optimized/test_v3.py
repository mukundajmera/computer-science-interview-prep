import os
import sys
import time
import threading
import pytest

def get_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

base_v3 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-optimized'))

log_level = get_module(os.path.join(base_v3, 'log_level.py'), 'log_level_v3')
logger_factory = get_module(os.path.join(base_v3, 'logger_factory.py'), 'logger_factory_v3')
appenders = get_module(os.path.join(base_v3, 'appenders.py'), 'appenders_v3')

sys.modules['log_level'] = log_level
sys.modules['logger_factory'] = logger_factory
sys.modules['appenders'] = appenders

@pytest.fixture(autouse=True)
def setup_teardown():
    logger_factory.LoggerFactory.reset()
    yield
    if logger_factory.LoggerFactory._instance is not None:
        logger_factory.LoggerFactory._instance.shutdown()

def test_async_batch_flushing():
    factory = logger_factory.LoggerFactory.get_instance()
    logger = factory.get_logger("test")
    logger.appenders.clear()
    
    appender = appenders.InMemoryAppender("Memory")
    logger.add_appender(appender)
    logger.set_level(log_level.LogLevel.INFO)
    
    thread_count = 10
    logs_per_thread = 50
    
    def log_task(thread_id):
        for j in range(logs_per_thread):
            logger.info(f"Thread {thread_id} batch log {j}")
            
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=log_task, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    time.sleep(1.5)
    
    logs = appender.get_logs()
    assert len(logs) == thread_count * logs_per_thread
