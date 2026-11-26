from ast_compiler import ASTCompiler, PromptSyntaxError
from prefix_cache_optimizer import PrefixCacheOptimizer, PromptSection

def main():
    print("--- AST Compiler Demo ---")
    template = """System: You are an assistant.
{#if use_tools}
Available tools:
{#for tool in tool_list}
- {tool}
{/for}
{/if}
User: {query}"""

    context = {
        "use_tools": True,
        "tool_list": ["Calculator", "WebSearch"],
        "query": "What is 2+2?"
    }

    try:
        ast = ASTCompiler.parse(template)
        rendered = ASTCompiler.render(ast, context)
        print("Rendered Template:")
        print(rendered)
    except PromptSyntaxError as e:
        print(f"Syntax Error: {e}")

    print("\n--- Prefix Cache Optimizer Demo ---")
    sections = [
        PromptSection(name="user", content="User: How do I cache?", is_static=False, priority=10),
        PromptSection(name="system", content="System: You are helpful.", is_static=True, priority=0),
        PromptSection(name="few_shot", content="User: Hi.\nSystem: Hello.", is_static=True, priority=1),
        PromptSection(name="context", content="Context: ...", is_static=False, priority=5)
    ]

    optimized = PrefixCacheOptimizer.optimize_order(sections)
    print("Optimized Order:")
    for sec in optimized:
        print(f"[{sec.is_static}] {sec.name} (Priority {sec.priority})")

if __name__ == "__main__":
    main()
