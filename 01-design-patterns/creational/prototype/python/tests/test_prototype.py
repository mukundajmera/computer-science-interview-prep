import os
import sys
from pathlib import Path
import importlib.util
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


proto_v1 = load_module("proto_v1", "python/v1-basic/prototype.py")
game_unit = load_module("game_unit", "python/v2-variant/game_unit_prototype.py")
config_mgr = load_module("config_mgr", "python/v3-advanced/config_snapshot_manager.py")


def test_shape_cloning_produces_independent_objects():
    orig_circle = proto_v1.Circle(20)
    orig_circle.set_color("blue").set_position(5, 10)
    cloned_circle = orig_circle.clone()

    assert cloned_circle is not orig_circle
    assert cloned_circle.radius == orig_circle.radius
    assert cloned_circle.color == orig_circle.color

    cloned_circle.set_position(99, 100)
    assert orig_circle.x == 5
    assert cloned_circle.x == 99

    orig_rect = proto_v1.Rectangle(30, 40).set_color("red")
    cloned_rect = orig_rect.clone()
    assert cloned_rect is not orig_rect
    assert cloned_rect.width == 30


def test_document_deep_copy_independence():
    doc = proto_v1.Document().set_title("Master").add_tag("v1").add_metadata("author", "Alice")
    clone = doc.clone()
    assert clone is not doc

    clone.set_title("Copy").add_tag("v2").add_metadata("editor", "Bob")
    assert "v2" not in doc.tags
    assert "editor" not in doc.metadata
    assert "v2" in clone.tags


def test_prototype_registry_lookup_and_missing_key():
    proto = proto_v1.Circle(12).set_color("purple")
    proto_v1.PrototypeRegistry.register("purple-circle-test", proto)

    assert proto_v1.PrototypeRegistry.contains("purple-circle-test") is True
    copy_circle = proto_v1.PrototypeRegistry.get_clone("purple-circle-test")
    assert copy_circle is not proto
    assert copy_circle.radius == 12

    with pytest.raises(ValueError):
        proto_v1.PrototypeRegistry.get_clone("unknown-key")


# --- v2-variant Tests ---

def test_game_unit_prototype_deep_copy_and_spawner():
    registry = game_unit.UnitSpawnerRegistry()
    warrior = game_unit.Warrior("Knight", 120, ["ShieldBash", "Cleave"])
    registry.register("knight", warrior)

    spawn1 = registry.spawn("knight")
    spawn2 = registry.spawn("knight")

    assert spawn1 is not warrior
    assert spawn2 is not spawn1
    assert spawn1.get_health() == 120

    spawn1.take_damage(40)
    assert spawn1.get_health() == 80
    assert spawn2.get_health() == 120

    spawn1.add_ability("Rally")
    assert "Rally" in spawn1.get_abilities()
    assert "Rally" not in spawn2.get_abilities()
    assert "Rally" not in warrior.get_abilities()

    with pytest.raises(ValueError):
        registry.spawn("nonexistent_unit")


# --- v3-advanced Tests ---

def test_config_snapshot_versioning_and_rollback():
    manager = config_mgr.ConfigurationManager(
        {"env": "staging", "db_host": "db-stage.internal"},
        {"pool_size": 10, "timeout": 2000}
    )
    assert manager.current.version == 1
    assert manager.current.get_property("db_host") == "db-stage.internal"

    manager.commitUpdate if hasattr(manager, "commitUpdate") else manager.commit_update(
        lambda draft: (draft.set_property("db_host", "db-prod.internal"), draft.set_limit("pool_size", 50))
    )
    assert manager.current.version == 2
    assert manager.current.get_property("db_host") == "db-prod.internal"
    assert manager.current.get_limit("pool_size") == 50
    assert manager.history_depth == 1

    success = manager.rollback()
    assert success is True
    assert manager.current.version == 1
    assert manager.current.get_property("db_host") == "db-stage.internal"
    assert manager.current.get_limit("pool_size") == 10

    # No more history to rollback
    assert manager.rollback() is False
