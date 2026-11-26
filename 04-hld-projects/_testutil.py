import importlib.util
import sys
import os

def load_module(path: str, module_name: str = None):
    """
    Load a module from a file path dynamically.
    Useful for importing modules from directories with hyphens.
    """
    if module_name is None:
        # Generate a module name based on path
        basename = os.path.basename(path)
        module_name = os.path.splitext(basename)[0]
        # Replace hyphens in the generated name if it's derived from a folder or file with hyphens
        module_name = module_name.replace('-', '_')

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Could not load module from {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
