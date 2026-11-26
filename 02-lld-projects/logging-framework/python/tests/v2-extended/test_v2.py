import os
import sys
import time
import tempfile
import pytest

def get_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

base_v2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-extended'))

log_level = get_module(os.path.join(base_v2, 'log_level.py'), 'log_level_v2')
logger_factory = get_module(os.path.join(base_v2, 'logger_factory.py'), 'logger_factory_v2')
appenders = get_module(os.path.join(base_v2, 'appenders.py'), 'appenders_v2')

sys.modules['log_level'] = log_level
sys.modules['logger_factory'] = logger_factory
sys.modules['appenders'] = appenders

@pytest.fixture(autouse=True)
def setup_teardown():
    logger_factory.LoggerFactory.reset()
    yield
    if logger_factory.LoggerFactory._instance is not None:
        logger_factory.LoggerFactory._instance.shutdown()

def test_composite_appender():
    appender1 = appenders.InMemoryAppender("Mem1")
    appender2 = appenders.InMemoryAppender("Mem2")
    composite = appenders.CompositeAppender("Composite", [appender1, appender2])
    
    factory = logger_factory.LoggerFactory.get_instance()
    logger = factory.get_logger("test")
    logger.appenders.clear()
    logger.add_appender(composite)
    logger.set_level(log_level.LogLevel.INFO)
    
    logger.info("Test message")
    time.sleep(0.1)
    
    assert len(appender1.get_logs()) == 1
    assert len(appender2.get_logs()) == 1

def test_rolling_file_appender():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.log")
        appender = appenders.RollingFileAppender("Rolling", filepath, 100, 2)
        
        factory = logger_factory.LoggerFactory.get_instance()
        logger = factory.get_logger("test")
        logger.appenders.clear()
        logger.add_appender(appender)
        logger.set_level(log_level.LogLevel.INFO)
        
        for i in range(10):
            logger.info("A somewhat long test message to force rolling " * 5 + str(i))
        
        time.sleep(0.5)
        
        assert os.path.exists(filepath)
        assert os.path.exists(filepath + ".1")

def test_appender_additivity():
    factory = logger_factory.LoggerFactory.get_instance()
    
    parent = factory.get_logger("com.parent")
    parent_appender = appenders.InMemoryAppender("ParentMemory")
    parent.add_appender(parent_appender)
    
    child = factory.get_logger("com.parent.child")
    child_appender = appenders.InMemoryAppender("ChildMemory")
    child.add_appender(child_appender)
    
    child.info("Hello Additivity")
    
    time.sleep(0.1)
    
    assert len(child_appender.get_logs()) == 1
    assert len(parent_appender.get_logs()) == 1
    
    child.additive = False
    child.info("No more parents")
    
    time.sleep(0.1)
    
    assert len(child_appender.get_logs()) == 2
    assert len(parent_appender.get_logs()) == 1

def test_hierarchical_level_inheritance():
    factory = logger_factory.LoggerFactory.get_instance()
    root = factory.get_logger("root")
    root.set_level(log_level.LogLevel.ERROR)
    
    parent = factory.get_logger("com.myapp")
    parent.set_level(log_level.LogLevel.DEBUG)
    
    child = factory.get_logger("com.myapp.service")
    
    assert root.get_effective_level() == log_level.LogLevel.ERROR
    assert parent.get_effective_level() == log_level.LogLevel.DEBUG
    assert child.get_effective_level() == log_level.LogLevel.DEBUG
    
    appender = appenders.InMemoryAppender("Memory")
    child.add_appender(appender)
    child.additive = False
    
    child.trace("Trace msg")
    child.info("Info msg")
    
    time.sleep(0.1)
    
    logs = appender.get_logs()
    assert len(logs) == 1
    assert logs[0].message == "Info msg"
