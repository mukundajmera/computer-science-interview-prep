import pytest
import importlib.util
import sys
import os

def load_v3():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    v3_dir = os.path.join(current_dir, '..', 'v3-optimized')
    
    # Load entities
    spec_entities = importlib.util.spec_from_file_location("entities_v3", os.path.join(v3_dir, 'entities.py'))
    entities = importlib.util.module_from_spec(spec_entities)
    sys.modules["entities"] = entities # Needs to be named 'entities' for config_engine to import it
    spec_entities.loader.exec_module(entities)
    
    # Load engine
    spec_engine = importlib.util.spec_from_file_location("config_engine_v3", os.path.join(v3_dir, 'config_engine.py'))
    config_engine = importlib.util.module_from_spec(spec_engine)
    sys.modules["config_engine"] = config_engine
    spec_engine.loader.exec_module(config_engine)
    
    return entities, config_engine.ConfigEngine

def test_evaluate_rollout():
    entities, ConfigEngine = load_v3()
    engine = ConfigEngine()
    
    bucket1 = entities.RolloutBucket(50, entities.Variant("A"))
    bucket2 = entities.RolloutBucket(50, entities.Variant("B"))
    rollout = entities.Rollout([bucket1, bucket2])
    
    rule = entities.Rule("country", entities.Operator.EQUALS, "US", rollout=rollout)
    flag = entities.FeatureFlag("experiment", entities.Variant("C"), [rule])
    engine.update_flag(flag)
    
    ctx1 = entities.UserContext("u1")
    ctx1.set_attribute("country", "US")
    
    result1 = engine.evaluate("experiment", ctx1)
    
    # Determinism test
    result2 = engine.evaluate("experiment", ctx1)
    assert result1.value == result2.value

def test_listener():
    entities, ConfigEngine = load_v3()
    engine = ConfigEngine()
    
    notified = {"status": False}
    def listener(flag):
        notified["status"] = True
        
    engine.register_listener("featureX", listener)
    
    flag = entities.FeatureFlag("featureX", entities.Variant(True))
    engine.update_flag(flag)
    
    assert notified["status"] is True
