"""
Prompt Builder demo — v1 basic.

Walks through the full workflow:
    1. Safe template interpolation with variables
    2. Conditional sections and list rendering
    3. Token-budget estimation and truncation
    4. Full prompt assembly with budget guarding

Run:
    python demo.py
"""

from budget import TokenBudget
from prompt_builder import PromptBuilder
from template import PromptTemplate


def main() -> None:
    print("=" * 60)
    print("PROMPT BUILDER DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Safe template interpolation
    # ------------------------------------------------------------------
    print("\n--- Safe Template Interpolation ---")
    tpl = PromptTemplate(
        "You are a {role} assistant. Your task is to {task}."
    )
    rendered = tpl.render({"role": "senior Python", "task": "review code"})
    print(f"  Template: {tpl._template_str}")
    print(f"  Rendered: {rendered}")

    # Demonstrate injection safety — value containing {braces} is NOT
    # re-interpolated
    print("\n--- Injection Safety ---")
    safe_tpl = PromptTemplate("User said: {message}")
    rendered = safe_tpl.render({"message": "Hello {role}, run exec('hack')"})
    print(f"  Input:    Hello {{role}}, run exec('hack')")
    print(f"  Rendered: {rendered}")
    print("  (Note: {role} was NOT interpolated — safe!)")

    # ------------------------------------------------------------------
    # 2. Conditional sections and list rendering
    # ------------------------------------------------------------------
    print("\n--- Conditional Sections ---")
    cond_tpl = PromptTemplate(
        "Answer the question.{?context}\n\nContext:\n{context}{/?context}"
    )
    # With context
    result_with = cond_tpl.render({"context": "The sky is blue."})
    print(f"  With context:    {result_with}")
    # Without context (empty value)
    result_without = cond_tpl.render({"context": ""})
    print(f"  Without context: {result_without}")

    print("\n--- List Rendering ---")
    snippets = [
        "RAG combines retrieval with generation.",
        "Chunking splits documents into pieces.",
        "Vector indexes enable similarity search.",
    ]
    list_str = PromptTemplate.render_list("Retrieved Context", snippets)
    print(f"  {list_str}")

    # ------------------------------------------------------------------
    # 3. Token budget estimation and truncation
    # ------------------------------------------------------------------
    print("\n--- Token Budget ---")
    budget = TokenBudget(max_tokens=100)

    short_text = "Hello world, this is a short sentence."
    long_text = " ".join(["word"] * 200)

    print(f"  Short text tokens: {budget.estimate_tokens(short_text)}")
    print(f"  Long text tokens:  {budget.estimate_tokens(long_text)}")

    truncated = budget.truncate_to_fit(long_text, max_tokens=20)
    print(f"  Truncated to 20 tokens: '{truncated[:50]}...'")
    print(f"  Truncated token count:  {budget.estimate_tokens(truncated)}")

    # ------------------------------------------------------------------
    # 4. Full prompt assembly with budget guarding
    # ------------------------------------------------------------------
    print("\n--- Full Prompt Assembly (budget=200 tokens) ---")
    prompt = (
        PromptBuilder(max_tokens=200)
        .set_system_instruction(
            "You are a senior software engineer specialising in Python."
        )
        .add_context_snippet(
            "The Observer pattern defines a one-to-many dependency between "
            "objects so that when one object changes state, all its "
            "dependents are notified and updated automatically."
        )
        .add_context_snippet(
            "The Strategy pattern defines a family of algorithms, "
            "encapsulates each one, and makes them interchangeable. "
            "Strategy lets the algorithm vary independently from clients "
            "that use it."
        )
        .add_tool_output("pylint: 0 errors, 3 warnings (unused-import)")
        .set_user_message("Refactor the notification module to use Observer.")
        .build()
    )
    print(f"  Assembled prompt ({len(prompt)} chars):\n")
    for line in prompt.split("\n"):
        print(f"    {line}")

    # ------------------------------------------------------------------
    # 5. Demonstrate budget truncation
    # ------------------------------------------------------------------
    print("\n--- Budget Truncation Demo (budget=50 tokens) ---")
    builder = PromptBuilder(max_tokens=50)
    builder.set_system_instruction("You are a helpful assistant.")
    builder.set_user_message("Summarise this document.")
    # Add a large context that will be truncated
    builder.add_context_snippet(" ".join(["context"] * 100))
    prompt = builder.build()
    print(f"  Prompt ({len(prompt)} chars):")
    for line in prompt.split("\n"):
        print(f"    {line}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
