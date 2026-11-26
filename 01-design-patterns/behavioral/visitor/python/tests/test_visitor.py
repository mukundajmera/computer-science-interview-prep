import os
import sys
from pathlib import Path
import importlib.util
import math
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


vis_v1 = load_module("vis_v1", "python/v1-basic/visitor_demo.py")
doc_vis = load_module("doc_vis", "python/v2-variant/document_export_visitor.py")
metrics_vis = load_module("metrics_vis", "python/v3-advanced/code_metrics_visitor.py")


def test_area_calculator_visits_all_shapes():
    circle = vis_v1.Circle(5.0)
    rect = vis_v1.Rectangle(4.0, 6.0)
    tri = vis_v1.Triangle(3.0, 4.0)

    calc = vis_v1.AreaCalculator()
    circle.accept(calc)
    rect.accept(calc)
    tri.accept(calc)

    expected = (math.pi * 25.0) + (24.0) + (0.5 * 3.0 * 4.0)
    assert calc.total_area == pytest.approx(expected, 0.01)


def test_drawing_visitor_executes():
    circle = vis_v1.Circle(3.0)
    rect = vis_v1.Rectangle(2.0, 5.0)
    tri = vis_v1.Triangle(4.0, 2.0)

    drawer = vis_v1.DrawingVisitor()
    circle.accept(drawer)
    rect.accept(drawer)
    tri.accept(drawer)


def test_polymorphic_shape_accept():
    shapes = [vis_v1.Circle(2.0), vis_v1.Rectangle(3.0, 4.0), vis_v1.Triangle(2.0, 3.0)]
    calc = vis_v1.AreaCalculator()
    for s in shapes:
        s.accept(calc)

    expected = (math.pi * 4.0) + (12.0) + (3.0)
    assert calc.total_area == pytest.approx(expected, 0.01)


# --- v2-variant Tests ---

def test_document_export_visitor():
    doc = [
        doc_vis.Heading("Overview", 2),
        doc_vis.Paragraph("Welcome to the platform."),
        doc_vis.CodeBlock("echo hello", "bash"),
        doc_vis.Hyperlink("Home", "https://home.io"),
    ]

    md_visitor = doc_vis.MarkdownExportVisitor()
    html_visitor = doc_vis.HtmlExportVisitor()

    for elem in doc:
        elem.accept(md_visitor)
        elem.accept(html_visitor)

    md_out = md_visitor.get_exported_output()
    assert "## Overview" in md_out
    assert "Welcome to the platform." in md_out
    assert "```bash\necho hello\n```" in md_out
    assert "[Home](https://home.io)" in md_out

    html_out = html_visitor.get_exported_output()
    assert "<h2>Overview</h2>" in html_out
    assert "<p>Welcome to the platform.</p>" in html_out
    assert '<code class="language-bash">echo hello</code>' in html_out
    assert '<a href="https://home.io">Home</a>' in html_out


# --- v3-advanced Tests ---

def test_ast_metrics_and_security_visitors():
    fn = metrics_vis.FunctionDef("handle_request", ["req"], [
        metrics_vis.Assignment("user", "req.get_user()"),
        metrics_vis.IfStatement(
            "user is None",
            then_branch=[metrics_vis.CallExpression("log_error", ["Unauthorized"])],
            else_branch=[
                metrics_vis.LoopStatement(
                    "while",
                    body=[metrics_vis.CallExpression("eval", ["req.code"])]
                )
            ]
        )
    ])

    metrics = metrics_vis.MetricsVisitor()
    security = metrics_vis.SecurityAuditVisitor()

    fn.accept(metrics)
    fn.accept(security)

    # Complexity: 1 (function) + 1 (if) + 1 (loop) = 3
    assert metrics.function_count == 1
    assert metrics.cyclomatic_complexity == 3
    assert metrics.statement_count >= 3

    # Security check catches eval
    assert len(security.security_alerts) == 1
    assert "eval" in security.security_alerts[0]
