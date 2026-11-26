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


af_v1 = load_module("af_v1", "python/v1-basic/abstract_factory.py")
db_factory = load_module("db_factory", "python/v2-variant/database_factory.py")
cloud_factory = load_module("cloud_factory", "python/v3-advanced/cloud_resource_factory.py")


def test_windows_factory_creates_windows_components():
    factory = af_v1.WindowsFactory()
    btn = factory.create_button()
    cb = factory.create_checkbox()
    tf = factory.create_text_field()

    assert isinstance(btn, af_v1.WindowsButton)
    assert isinstance(cb, af_v1.WindowsCheckbox)
    assert isinstance(tf, af_v1.WindowsTextField)

    assert cb.is_checked() is False
    cb.toggle()
    assert cb.is_checked() is True

    tf.set_value("win_test")
    assert tf.get_value() == "win_test"


def test_mac_factory_creates_mac_components():
    factory = af_v1.MacFactory()
    btn = factory.create_button()
    cb = factory.create_checkbox()
    tf = factory.create_text_field()

    assert isinstance(btn, af_v1.MacButton)
    assert isinstance(cb, af_v1.MacCheckbox)
    assert isinstance(tf, af_v1.MacTextField)

    assert cb.is_checked() is False
    cb.toggle()
    assert cb.is_checked() is True

    tf.set_value("mac_test")
    assert tf.get_value() == "mac_test"


def test_gui_factory_provider_resolves_and_validates():
    win_f = af_v1.GUIFactoryProvider.get_factory("windows")
    assert isinstance(win_f, af_v1.WindowsFactory)

    mac_f = af_v1.GUIFactoryProvider.get_factory("mac")
    assert isinstance(mac_f, af_v1.MacFactory)

    with pytest.raises(ValueError):
        af_v1.GUIFactoryProvider.get_factory("unsupported_os")


# --- v2-variant Tests ---

def test_database_factories_execute_dialect_specific_operations():
    pg_factory = db_factory.PostgresFactory()
    pg_conn = pg_factory.create_connection()
    pg_cmd = pg_factory.create_command()
    pg_tx = pg_factory.create_transaction()

    assert pg_conn.get_dialect() == "POSTGRESQL"
    assert pg_conn.is_open() is False
    pg_conn.open()
    assert pg_conn.is_open() is True
    assert "[PostgreSQL Executed]" in pg_cmd.execute("SELECT 1")
    assert pg_tx.is_active() is False
    pg_tx.begin()
    assert pg_tx.is_active() is True
    pg_tx.commit()
    assert pg_tx.is_active() is False

    mysql_factory = db_factory.MySqlFactory()
    mysql_conn = mysql_factory.create_connection()
    mysql_cmd = mysql_factory.create_command()
    assert mysql_conn.get_dialect() == "MYSQL"
    assert "[MySQL Executed]" in mysql_cmd.execute("SELECT 1")


# --- v3-advanced Tests ---

def test_cloud_resource_factories_and_registry():
    aws = cloud_factory.CloudProviderRegistry.get_factory("aws")
    assert aws.get_provider() == "AWS"
    vm = aws.create_compute()
    assert vm.get_status() == "STOPPED"
    launch_res = vm.launch("m5.large")
    assert "aws-ec2-m5.large" in launch_res
    assert vm.get_status() == "RUNNING"

    s3 = aws.create_storage()
    s3.put_object("my-bucket", "config.json", b'{"key": "val"}')
    assert s3.get_object("my-bucket", "config.json") == b'{"key": "val"}'

    vault = aws.create_key_vault()
    vault.set_secret("db_pass", "super_secret")
    assert vault.get_secret("db_pass") == "super_secret"

    gcp = cloud_factory.CloudProviderRegistry.get_factory("gcp")
    assert gcp.get_provider() == "GCP"
    gce = gcp.create_compute()
    assert "gcp-gce-n2-standard" in gce.launch("n2-standard")

    with pytest.raises(ValueError):
        cloud_factory.CloudProviderRegistry.get_factory("azure_not_registered")
