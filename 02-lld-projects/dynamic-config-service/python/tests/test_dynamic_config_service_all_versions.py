import unittest
import os
import sys
import importlib.util

def load_v1():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    v1_dir = os.path.join(current_dir, '..', 'v1-basic')
    spec = importlib.util.spec_from_file_location("config_engine", os.path.join(v1_dir, 'config_engine.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules["config_engine"] = module
    spec.loader.exec_module(module)
    return module

class TestDynamicConfigService(unittest.TestCase):
    def test_cross_language_hash_determinism(self):
        mod = load_v1()
        flag = mod.FeatureFlag("experiment", mod.Variant("A"), 50)
        snap = mod.ConfigSnapshot(1, {"experiment": flag})
        service = mod.DynamicConfigService(snap)
        
        ctx1 = mod.UserContext("u1")
        result1 = service.evaluate("experiment", ctx1, mod.Variant("Fallback"))
        self.assertEqual(result1.value, "A")
        
        ctx2 = mod.UserContext("u3")
        result2 = service.evaluate("experiment", ctx2, mod.Variant("Fallback"))
        self.assertEqual(result2.value, "Fallback")

    def test_atomic_snapshots_and_rollback_and_stale(self):
        mod = load_v1()
        flag_v1 = mod.FeatureFlag("f1", mod.Variant("V1"), 100)
        snap1 = mod.ConfigSnapshot(1, {"f1": flag_v1})
        service = mod.DynamicConfigService(snap1)
        
        ctx = mod.UserContext("u1")
        self.assertEqual(service.evaluate("f1", ctx, mod.Variant(None)).value, "V1")
        
        flag_v2 = mod.FeatureFlag("f1", mod.Variant("V2"), 100)
        snap2 = mod.ConfigSnapshot(2, {"f1": flag_v2})
        
        self.assertTrue(service.apply_snapshot(snap2))
        self.assertEqual(service.evaluate("f1", ctx, mod.Variant(None)).value, "V2")
        
        snap_stale = mod.ConfigSnapshot(1, {"f1": flag_v1})
        self.assertFalse(service.apply_snapshot(snap_stale))
        self.assertEqual(service.evaluate("f1", ctx, mod.Variant(None)).value, "V2")
        
        self.assertTrue(service.rollback(1))
        self.assertEqual(service.evaluate("f1", ctx, mod.Variant(None)).value, "V1")
        self.assertFalse(service.rollback(999))

    def test_missing_flag(self):
        mod = load_v1()
        service = mod.DynamicConfigService(mod.ConfigSnapshot(1, {}))
        fallback = mod.Variant("fallback_val")
        self.assertEqual(service.evaluate("missing", mod.UserContext("u1"), fallback).value, "fallback_val")

    def test_invalid_percentage(self):
        mod = load_v1()
        flag = mod.FeatureFlag("f1", mod.Variant("default"), 150)
        snap = mod.ConfigSnapshot(1, {"f1": flag})
        service = mod.DynamicConfigService(snap)
        ctx = mod.UserContext("u1")
        result = service.evaluate("f1", ctx, mod.Variant("fb"))
        self.assertEqual(result.value, "fb")

    def test_tenant_override_precedence(self):
        mod = load_v1()
        overrides = {"tenantA": mod.Variant("override_val")}
        flag = mod.FeatureFlag("f1", mod.Variant("def"), 100, overrides)
        snap = mod.ConfigSnapshot(1, {"f1": flag})
        service = mod.DynamicConfigService(snap)
        
        ctx = mod.UserContext("u1")
        ctx.set_attribute("tenant", "tenantA")
        self.assertEqual(service.evaluate("f1", ctx, mod.Variant("fb")).value, "override_val")

if __name__ == '__main__':
    unittest.main()
