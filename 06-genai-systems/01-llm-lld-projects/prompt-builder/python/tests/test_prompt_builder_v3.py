import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from ast_compiler import ASTCompiler, PromptSyntaxError
from prefix_cache_optimizer import PrefixCacheOptimizer, PromptSection

def test_ast_compiler_basic_variables():
    template = "Hello {name}, your score is {score}."
    context = {"name": "Alice", "score": 42}
    ast = ASTCompiler.parse(template)
    rendered = ASTCompiler.render(ast, context)
    assert rendered == "Hello Alice, your score is 42."

def test_ast_compiler_conditionals():
    template = "Start {#if show}Visible{/if} End"
    ast = ASTCompiler.parse(template)

    rendered_true = ASTCompiler.render(ast, {"show": True})
    assert rendered_true == "Start Visible End"

    rendered_false = ASTCompiler.render(ast, {"show": False})
    assert rendered_false == "Start  End"

def test_ast_compiler_loops():
    template = "Items: {#for item in items}- {item}\n{/for}"
    ast = ASTCompiler.parse(template)
    rendered = ASTCompiler.render(ast, {"items": ["apple", "banana"]})
    assert rendered == "Items: - apple\n- banana\n"

def test_ast_compiler_syntax_error():
    with pytest.raises(PromptSyntaxError):
        ASTCompiler.parse("{#if show} content")

    with pytest.raises(PromptSyntaxError):
        ASTCompiler.parse("content {/if}")

def test_prefix_cache_optimizer_ordering():
    sections = [
        PromptSection(name="dynamic_user", content="user", is_static=False, priority=10),
        PromptSection(name="static_few_shot", content="few_shot", is_static=True, priority=1),
        PromptSection(name="static_system", content="system", is_static=True, priority=0),
        PromptSection(name="dynamic_context", content="context", is_static=False, priority=5)
    ]

    optimized = PrefixCacheOptimizer.optimize_order(sections)

    assert [s.name for s in optimized] == [
        "static_system",
        "static_few_shot",
        "dynamic_context",
        "dynamic_user"
    ]

def test_prefix_cache_optimizer_cacheable_prefix():
    sections = [
        PromptSection(name="user", content="How do?", is_static=False, priority=10),
        PromptSection(name="sys", content="Sys prompt.", is_static=True, priority=0),
        PromptSection(name="few", content="Ex1.", is_static=True, priority=1)
    ]
    prefix = PrefixCacheOptimizer.get_cacheable_prefix(sections)
    assert prefix == "Sys prompt.\n\nEx1."
