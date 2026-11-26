"""Helpers for importing versioned Python examples without sys.path leakage."""

from __future__ import annotations

import importlib
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Iterable


_MISSING = object()


@contextmanager
def isolated_module_path(version_dir: Path, module_names: Iterable[str]):
    """Temporarily import bare modules from one version directory."""
    resolved_dir = str(version_dir.resolve())
    old_path = sys.path[:]
    saved_modules = {name: sys.modules.get(name, _MISSING) for name in module_names}
    for name in module_names:
        sys.modules.pop(name, None)
    sys.path.insert(0, resolved_dir)
    try:
        yield
    finally:
        sys.path[:] = old_path
        for name, module in saved_modules.items():
            if module is _MISSING:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def assert_module_from(module: ModuleType, version_dir: Path) -> None:
    module_file = Path(module.__file__).resolve()
    expected_dir = version_dir.resolve()
    if expected_dir not in module_file.parents:
        raise AssertionError(f"{module.__name__} loaded from {module_file}, expected under {expected_dir}")


def import_modules_from(
    version_dir: Path,
    module_names: Iterable[str],
    *,
    purge_modules: Iterable[str] | None = None,
) -> dict[str, ModuleType]:
    purge_names = set(purge_modules or ()) | set(module_names)
    with isolated_module_path(version_dir, purge_names):
        modules = {name: importlib.import_module(name) for name in module_names}
    for module in modules.values():
        assert_module_from(module, version_dir)
    return modules
