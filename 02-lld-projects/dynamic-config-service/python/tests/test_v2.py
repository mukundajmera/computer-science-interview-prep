import pytest
import importlib.util
import sys
import os

def load_v2():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    v2_dir = os.path.join(current_dir, '..', 'v2-extended')
    
    # Load entities
    spec_entities = importlib.util.spec_from_file_location("entities", os.path.join(v2_dir, 'entities.py'))
    entities = importlib.util.module_from_spec(spec_entities)
    sys.modules["entities"] = entities
    spec_entities.loader.exec_module(entities)
    
    # Load engine
    spec_engine = importlib.util.spec_from_file_location("config_engine", os.path.join(v2_dir, 'config_engine.py'))
    config_engine = importlib.util.module_from_spec(spec_engine)
    sys.modules["config_engine"] = config_engine
    spec_engine.loader.exec_module(config_engine)
    
    return entities, config_engine.ConfigEngine

def test_evaluate_default():
    entities, ConfigEngine = load_v2()
    engine = ConfigEngine()
    
    flag = entities.FeatureFlag("color", entities.Variant("blue"))
    engine.update_flag(flag)
    
    ctx = entities.UserContext("u1")
    result = engine.evaluate("color", ctx)
    assert result.value == "blue"

def test_evaluate_rule_matches():
    entities, ConfigEngine = load_v2()
    engine = ConfigEngine()
    
    rule = entities.Rule("country", entities.Operator.EQUALS, "US", entities.Variant("red"))
    flag = entities.FeatureFlag("color", entities.Variant("blue"), [rule])
    engine.update_flag(flag)
    
    ctx = entities.UserContext("u1")
    ctx.set_attribute("country", "US")
    
    result = engine.evaluate("color", ctx)
    assert result.value == "red"

def test_evaluate_rule_does_not_match():
    entities, ConfigEngine = load_v2()
    engine = ConfigEngine()
    
    rule = entities.Rule("country", entities.Operator.EQUALS, "US", entities.Variant("red"))
    flag = entities.FeatureFlag("color", entities.Variant("blue"), [rule])
    engine.update_flag(flag)
    
    ctx = entities.UserContext("u1")
    ctx.set_attribute("country", "UK")
    
    result = engine.evaluate("color", ctx)
    assert result.value == "blue"
