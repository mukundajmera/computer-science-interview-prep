import sys
import os
import pytest

# Add v1-basic to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from coding_copilot_service import (
    ContextAssemblyEngine,
    PrefixCacheSimulator,
    MultiModelRouter,
    CompletionPostProcessor,
    CodingCopilotService
)

def test_context_assembly_engine():
    engine = ContextAssemblyEngine()
    prefix = "def add(a, b):"
    suffix = "    return c"
    recent_edits = ["# Added new math functions"]
    open_file_imports = ["import math"]

    context = engine.assemble(prefix, suffix, recent_edits, open_file_imports)

    assert "<|imports|>\nimport math" in context
    assert "<|recent_edits|>\n# Added new math functions" in context
    assert "<|fim_prefix|>\ndef add(a, b):\n<|fim_suffix|>\n    return c\n<|fim_middle|>" in context

def test_prefix_cache_simulator():
    cache = PrefixCacheSimulator()
    prefix = "def calculate():"
    completion = "    pass"

    assert cache.get(prefix) is None

    cache.put(prefix, completion)

    assert cache.get(prefix) == completion
    assert cache.get("def other():") is None

def test_multi_model_router():
    router = MultiModelRouter(latency_budget_ms=300)

    # Should trigger "def " fast model logic and then verified
    context = "def my_func():"
    result = router.generate(context)
    assert result == "    return True  # Verified"

    # Not containing "def "
    context_no_def = "class MyClass:"
    result_no_def = router.generate(context_no_def)
    assert result_no_def == "    pass"

def test_completion_post_processor():
    processor = CompletionPostProcessor()

    # Test syntax truncate
    text_with_newline = "    return True\n\n    # Should be removed"
    processed1 = processor.process(text_with_newline)
    assert "Should be removed" not in processed1

    # Test bracket balance
    text_unbalanced = "    data = {'key': 'value'"
    processed2 = processor.process(text_unbalanced)
    assert processed2 == "    data = {'key': 'value'}"

    text_unbalanced_list = "    lst = [1, 2"
    processed3 = processor.process(text_unbalanced_list)
    assert processed3 == "    lst = [1, 2]"

def test_coding_copilot_service_integration():
    service = CodingCopilotService()

    prefix = "def generate_token():"
    suffix = ""

    # First call (cache miss)
    result1 = service.get_completion(prefix, suffix)
    assert result1 == "    return True  # Verified"

    # Second call (cache hit)
    # Even if we change context slightly, cache is based on prefix
    result2 = service.get_completion(prefix, suffix, recent_edits=["# random string"])
    assert result2 == "    return True  # Verified"

    # Let's ensure cache works by giving it a prefix that wouldn't normally get Verified
    prefix2 = "class Generator:"
    service.cache.put(prefix2, "    cached_result")
    result3 = service.get_completion(prefix2, suffix)
    assert result3 == "    cached_result"
