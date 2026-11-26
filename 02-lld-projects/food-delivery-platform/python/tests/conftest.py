import os
import sys
import types
import importlib.util

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for ver, folder in [("v1_basic", "v1-basic"), ("v2_extended", "v2-extended"), ("v3_optimized", "v3-optimized")]:
    models_path = os.path.join(base_dir, folder, "models.py")
    if os.path.exists(models_path):
        spec = importlib.util.spec_from_file_location(f"{ver}.models", models_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        pkg = types.ModuleType(ver)
        pkg.models = mod
        sys.modules[ver] = pkg
        sys.modules[f"{ver}.models"] = mod
