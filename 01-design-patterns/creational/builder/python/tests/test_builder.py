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


builder_v1 = load_module("builder_v1", "python/v1-basic/builder.py")
doc_director = load_module("doc_director", "python/v2-variant/document_director.py")
type_safe_builder = load_module("type_safe_builder", "python/v3-advanced/type_safe_builder.py")


def test_pizza_builder_constructs_pizza():
    pizza = (
        builder_v1.Pizza.Builder("large")
        .crust("thin")
        .sauce("bbq")
        .add_topping("mushrooms")
        .add_topping("olives")
        .extra_cheese()
        .gluten_free()
        .build()
    )

    assert pizza.size == "large"
    assert pizza.crust == "thin"
    assert pizza.sauce == "bbq"
    assert "mushrooms" in pizza.toppings
    assert "olives" in pizza.toppings
    assert pizza.extra_cheese is True
    assert pizza.gluten_free is True


def test_pizza_builder_requires_size():
    with pytest.raises(ValueError):
        builder_v1.Pizza.Builder("").build()


def test_computer_builder_validates_ram_and_http_request():
    with pytest.raises(ValueError):
        builder_v1.Computer.Builder("Intel i3", 2).build()

    comp = builder_v1.Computer.Builder("Intel i7", 16).storage(512).gpu("RTX 4080").no_bluetooth().no_wifi().build()
    assert comp.ram == 16
    assert comp.bluetooth is False

    req = builder_v1.HttpRequest("https://example.com/api").post().with_header("Auth", "secret").build()
    assert req.method == "POST"
    assert req.headers.get("Auth") == "secret"


# --- v2-variant Tests ---

def test_document_director_html_and_markdown_variants():
    html_builder = doc_director.HtmlDocumentBuilder()
    director = doc_director.DocumentDirector(html_builder)

    findings = ["Cache hit ratio improved to 95%", "p99 latency reduced by 30ms"]
    html_out = director.construct_report("Audit Report", findings, "Signed by Team Lead")
    assert "<article>" in html_out
    assert "<h1>Audit Report</h1>" in html_out
    assert "<h2>Finding 1</h2>" in html_out
    assert "<footer>Signed by Team Lead</footer>" in html_out

    md_builder = doc_director.MarkdownDocumentBuilder()
    director.change_builder(md_builder)
    md_out = director.construct_summary("Executive Brief", "All systems operational.")
    assert md_out.startswith("# Executive Brief")
    assert "## Executive Summary" in md_out
    assert "*Confidential*" in md_out


# --- v3-advanced Tests ---

def test_staged_query_builder_validates_clauses():
    query = (
        type_safe_builder.StagedQueryBuilder.select("id", "name", "email")
        .from_table("users")
        .where("status = 'active'")
        .limit(25)
        .build()
    )
    assert query.to_sql() == "SELECT id, name, email FROM users WHERE status = 'active' LIMIT 25"
    assert query.columns == ("id", "name", "email")
    assert query.table == "users"


def test_staged_query_builder_rejection_on_invalid_inputs():
    with pytest.raises(ValueError):
        type_safe_builder.StagedQueryBuilder.select()

    with pytest.raises(ValueError):
        type_safe_builder.StagedQueryBuilder.select("id").from_table("")

    with pytest.raises(ValueError):
        type_safe_builder.StagedQueryBuilder.select("id").from_table("users").limit(-1)
