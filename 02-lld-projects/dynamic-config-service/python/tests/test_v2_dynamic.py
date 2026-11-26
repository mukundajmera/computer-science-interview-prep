import unittest
import os
import sys
import importlib.util

def load_v2():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    v2_dir = os.path.join(current_dir, '..', 'v2-extended')
    
    spec_entities = importlib.util.spec_from_file_location("entities", os.path.join(v2_dir, 'entities.py'))
    entities = importlib.util.module_from_spec(spec_entities)
    sys.modules["entities"] = entities
    spec_entities.loader.exec_module(entities)
    
    spec_service = importlib.util.spec_from_file_location("dynamic_config_service", os.path.join(v2_dir, 'dynamic_config_service.py'))
    service = importlib.util.module_from_spec(spec_service)
    sys.modules["dynamic_config_service"] = service
    spec_service.loader.exec_module(service)
    
    return entities, service

class TestDynamicConfigServiceV2(unittest.TestCase):
    def test_cross_language_hash_determinism(self):
        entities, service = load_v2()
        flag = entities.FeatureFlag("experiment", entities.Variant("A"), None, 50, None)
        snap = service.ConfigSnapshot(1, {"experiment": flag})
        svc = service.DynamicConfigService(snap)
        
        ctx1 = entities.UserContext("u1")
        result1 = svc.evaluate("experiment", ctx1, entities.Variant("Fallback"))
        self.assertEqual(result1.value, "A")
        
        ctx2 = entities.UserContext("u3")
        result2 = svc.evaluate("experiment", ctx2, entities.Variant("Fallback"))
        self.assertEqual(result2.value, "Fallback")

    def test_atomic_snapshots_and_rollback_and_stale(self):
        entities, service = load_v2()
        flag_v1 = entities.FeatureFlag("f1", entities.Variant("V1"), None, 100, None)
        snap1 = service.ConfigSnapshot(1, {"f1": flag_v1})
        svc = service.DynamicConfigService(snap1)
        
        ctx = entities.UserContext("u1")
        self.assertEqual(svc.evaluate("f1", ctx, entities.Variant(None)).value, "V1")
        
        flag_v2 = entities.FeatureFlag("f1", entities.Variant("V2"), None, 100, None)
        snap2 = service.ConfigSnapshot(2, {"f1": flag_v2})
        
        self.assertTrue(svc.apply_snapshot(snap2))
        self.assertEqual(svc.evaluate("f1", ctx, entities.Variant(None)).value, "V2")
        
        snap_stale = service.ConfigSnapshot(1, {"f1": flag_v1})
        self.assertFalse(svc.apply_snapshot(snap_stale))
        self.assertEqual(svc.evaluate("f1", ctx, entities.Variant(None)).value, "V2")
        
        self.assertTrue(svc.rollback(1))
        self.assertEqual(svc.evaluate("f1", ctx, entities.Variant(None)).value, "V1")
        self.assertFalse(svc.rollback(999))

    def test_missing_flag(self):
        entities, service = load_v2()
        svc = service.DynamicConfigService(service.ConfigSnapshot(1, {}))
        fallback = entities.Variant("fallback_val")
        self.assertEqual(svc.evaluate("missing", entities.UserContext("u1"), fallback).value, "fallback_val")

    def test_invalid_percentage(self):
        entities, service = load_v2()
        flag = entities.FeatureFlag("f1", entities.Variant("default"), None, 150, None)
        snap = service.ConfigSnapshot(1, {"f1": flag})
        svc = service.DynamicConfigService(snap)
        ctx = entities.UserContext("u1")
        result = svc.evaluate("f1", ctx, entities.Variant("fb"))
        self.assertEqual(result.value, "fb")

    def test_tenant_override_precedence(self):
        entities, service = load_v2()
        overrides = {"tenantA": entities.Variant("override_val")}
        flag = entities.FeatureFlag("f1", entities.Variant("def"), None, 100, overrides)
        snap = service.ConfigSnapshot(1, {"f1": flag})
        svc = service.DynamicConfigService(snap)
        
        ctx = entities.UserContext("u1")
        ctx.set_attribute("tenant", "tenantA")
        self.assertEqual(svc.evaluate("f1", ctx, entities.Variant("fb")).value, "override_val")

if __name__ == '__main__':
    unittest.main()
