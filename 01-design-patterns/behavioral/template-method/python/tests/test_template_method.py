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


tm_v1 = load_module("tm_v1", "python/v1-basic/template_method_demo.py")
etl = load_module("etl", "python/v2-variant/etl_pipeline.py")
payment = load_module("payment", "python/v3-advanced/payment_transaction_template.py")


def test_csv_processor_execution():
    processor = tm_v1.CSVProcessor()
    assert isinstance(processor, tm_v1.DataProcessor)
    processor.process_data()


def test_json_processor_execution():
    processor = tm_v1.JSONProcessor()
    assert isinstance(processor, tm_v1.DataProcessor)
    processor.process_data()


def test_xml_processor_execution():
    processor = tm_v1.XMLProcessor()
    assert isinstance(processor, tm_v1.DataProcessor)
    processor.process_data()


# --- v2-variant Tests ---

def test_etl_pipeline_lifecycle_and_hooks():
    sales = etl.EcommerceSalesEtl()
    success = sales.run_pipeline("s3://sales/input.csv", "snowflake://analytics")
    assert success is True
    assert any("Started" in l for l in sales.execution_log)
    assert any("Extracted 3 records" in l for l in sales.execution_log)
    assert any("Cleanup hook executed" in l for l in sales.execution_log)

    audit_failing = etl.StrictAuditLogEtl(fail_validation=True)
    assert audit_failing.run_pipeline("log://audit", "sec://archive") is False
    assert any("Validation failed" in l for l in audit_failing.execution_log)


# --- v3-advanced Tests ---

def test_payment_transaction_template_success_and_compensation():
    card = payment.CreditCardProcessor()
    res1 = card.process_payment("TXN-101", 250.0, "USD")
    assert res1.success is True
    assert res1.message == "Success"
    assert any("Audit record stored" in l for l in res1.audit_logs)

    # Fraud hook triggers on large amounts >= 10,000
    res_fraud = card.process_payment("TXN-102", 15000.0, "USD")
    assert res_fraud.success is False
    assert res_fraud.message == "Fraud check failed"
    assert any("Compensation executed" in l for l in res_fraud.audit_logs)

    # Debit failure triggers compensation hook
    crypto_fail = payment.HighRiskCryptoProcessor(simulate_network_drop=True)
    res_debit_fail = crypto_fail.process_payment("TXN-103", 500.0, "ETH")
    assert res_debit_fail.success is False
    assert res_debit_fail.message == "Payment debit declined"
    assert any("Compensation executed" in l for l in res_debit_fail.audit_logs)
