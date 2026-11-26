"""
Tests for Prompt Builder (v1-basic).
"""
import unittest
import sys
import os

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestPromptTemplate(unittest.TestCase):
    """Tests for PromptTemplate safe interpolation."""

    def setUp(self):
        from template import PromptTemplate, TemplateVariable
        self.PromptTemplate = PromptTemplate
        self.TemplateVariable = TemplateVariable

    def test_basic_interpolation(self):
        """Simple placeholders should be replaced with provided values."""
        tpl = self.PromptTemplate("Hello, {name}!")
        result = tpl.render({"name": "Alice"})
        self.assertEqual(result, "Hello, Alice!")

    def test_multiple_placeholders(self):
        """Multiple distinct placeholders should all be substituted."""
        tpl = self.PromptTemplate("{greeting}, {name}! You are a {role}.")
        result = tpl.render({
            "greeting": "Hi",
            "name": "Bob",
            "role": "developer",
        })
        self.assertEqual(result, "Hi, Bob! You are a developer.")

    def test_injection_safety_no_reinterpolation(self):
        """Values containing placeholder syntax must NOT be re-interpolated."""
        tpl = self.PromptTemplate("User said: {message}")
        result = tpl.render({"message": "Hello {role}"})
        self.assertEqual(result, "User said: Hello {role}")

    def test_injection_safety_no_code_execution(self):
        """Values with executable-looking strings must be treated as text."""
        tpl = self.PromptTemplate("Input: {data}")
        result = tpl.render({"data": "__import__('os').system('rm -rf /')"})
        self.assertIn("__import__", result)

    def test_missing_required_variable_raises(self):
        """Strict mode should raise ValueError for missing required vars."""
        tpl = self.PromptTemplate("{name} is {role}")
        with self.assertRaises(ValueError):
            tpl.render({"name": "Alice"})

    def test_lenient_mode_missing_variable(self):
        """Non-strict mode should replace missing vars with defaults."""
        tpl = self.PromptTemplate("{name} is {role}", strict=False)
        result = tpl.render({"name": "Alice"})
        self.assertEqual(result, "Alice is ")

    def test_empty_template_raises(self):
        """Empty template string should raise ValueError."""
        with self.assertRaises(ValueError):
            self.PromptTemplate("")

    def test_conditional_section_included(self):
        """Conditional section should appear when variable has a value."""
        tpl = self.PromptTemplate("Base.{?extra} Extra: {extra}{/?extra}")
        result = tpl.render({"extra": "details"})
        self.assertIn("Extra: details", result)

    def test_conditional_section_excluded(self):
        """Conditional section should be stripped when variable is empty."""
        tpl = self.PromptTemplate("Base.{?extra} Extra: {extra}{/?extra}")
        result = tpl.render({"extra": ""})
        self.assertEqual(result, "Base.")

    def test_render_list_helper(self):
        """render_list should format items with bullets and a header."""
        result = self.PromptTemplate.render_list(
            "Items", ["one", "two", "three"]
        )
        self.assertIn("Items:", result)
        self.assertIn("- one", result)
        self.assertIn("- two", result)
        self.assertIn("- three", result)

    def test_render_list_empty(self):
        """render_list with empty list should return empty string."""
        result = self.PromptTemplate.render_list("Items", [])
        self.assertEqual(result, "")

    def test_escaped_braces(self):
        """Double braces should be rendered as literal single braces."""
        tpl = self.PromptTemplate("Use {{variable}} syntax. Name: {name}")
        result = tpl.render({"name": "test"})
        self.assertIn("{variable}", result)
        self.assertIn("Name: test", result)

    def test_get_variable_names(self):
        """get_variable_names should return all placeholder names."""
        tpl = self.PromptTemplate("{a} and {b} and {a}")
        names = tpl.get_variable_names()
        self.assertEqual(names, {"a", "b"})


class TestTokenBudget(unittest.TestCase):
    """Tests for TokenBudget estimation and truncation."""

    def setUp(self):
        from budget import TokenBudget, BudgetAllocation, default_token_estimator
        self.TokenBudget = TokenBudget
        self.BudgetAllocation = BudgetAllocation
        self.default_token_estimator = default_token_estimator

    def test_default_estimator_nonempty(self):
        """Default estimator should return positive count for non-empty text."""
        budget = self.TokenBudget(max_tokens=1000)
        tokens = budget.estimate_tokens("Hello world, this is a test.")
        self.assertGreater(tokens, 0)

    def test_default_estimator_empty(self):
        """Default estimator should return 0 for empty text."""
        budget = self.TokenBudget(max_tokens=1000)
        self.assertEqual(budget.estimate_tokens(""), 0)
        self.assertEqual(budget.estimate_tokens("   "), 0)

    def test_invalid_max_tokens_raises(self):
        """Zero or negative max_tokens should raise ValueError."""
        with self.assertRaises(ValueError):
            self.TokenBudget(max_tokens=0)
        with self.assertRaises(ValueError):
            self.TokenBudget(max_tokens=-10)

    def test_allocate_and_fits(self):
        """Text should fit if its tokens are within the section allocation."""
        budget = self.TokenBudget(max_tokens=1000)
        budget.allocate("system", 100)
        short = "A short instruction."
        long = " ".join(["word"] * 200)
        self.assertTrue(budget.fits("system", short))
        self.assertFalse(budget.fits("system", long))

    def test_truncate_to_fit(self):
        """Truncation should reduce token count to within the limit."""
        budget = self.TokenBudget(max_tokens=1000)
        long_text = " ".join(["word"] * 200)
        truncated = budget.truncate_to_fit(long_text, max_tokens=20)
        self.assertLessEqual(budget.estimate_tokens(truncated), 20)
        self.assertGreater(len(truncated), 0)

    def test_truncate_preserves_short_text(self):
        """Text already within budget should be returned unchanged."""
        budget = self.TokenBudget(max_tokens=1000)
        short = "Short text."
        result = budget.truncate_to_fit(short, max_tokens=100)
        self.assertEqual(result, short)

    def test_total_used_and_remaining(self):
        """total_used and total_remaining should reflect recorded usage."""
        budget = self.TokenBudget(max_tokens=100)
        budget.allocate("a", 50)
        budget.allocate("b", 50)
        budget.record_usage("a", "some text here")
        used_a = budget.get_allocation("a").used_tokens
        self.assertGreater(used_a, 0)
        self.assertEqual(budget.total_used(), used_a)
        self.assertEqual(budget.total_remaining(), 100 - used_a)

    def test_custom_estimator(self):
        """Custom estimator should override the default heuristic."""
        # Estimator that counts characters instead of words
        budget = self.TokenBudget(
            max_tokens=1000,
            token_estimator=lambda text: len(text),
        )
        self.assertEqual(budget.estimate_tokens("abc"), 3)

    def test_budget_allocation_remaining(self):
        """BudgetAllocation.remaining() should be max - used."""
        alloc = self.BudgetAllocation("test", max_tokens=100, used_tokens=40)
        self.assertEqual(alloc.remaining(), 60)

    def test_allocation_remaining_never_negative(self):
        """remaining() should not go below zero."""
        alloc = self.BudgetAllocation("test", max_tokens=10, used_tokens=50)
        self.assertEqual(alloc.remaining(), 0)

    def test_truncate_to_zero(self):
        """Truncation to 0 tokens should return empty string."""
        budget = self.TokenBudget(max_tokens=1000)
        result = budget.truncate_to_fit("Some text here", max_tokens=0)
        self.assertEqual(result, "")


class TestPromptBuilder(unittest.TestCase):
    """Tests for PromptBuilder assembly and budget enforcement."""

    def setUp(self):
        from prompt_builder import PromptBuilder, PromptSection
        self.PromptBuilder = PromptBuilder
        self.PromptSection = PromptSection

    def test_basic_build(self):
        """Build with system + user should produce a prompt with both."""
        prompt = (
            self.PromptBuilder(max_tokens=4096)
            .set_system_instruction("You are helpful.")
            .set_user_message("Hello!")
            .build()
        )
        self.assertIn("You are helpful.", prompt)
        self.assertIn("Hello!", prompt)

    def test_section_order(self):
        """System should come before user in the final prompt."""
        prompt = (
            self.PromptBuilder(max_tokens=4096)
            .set_system_instruction("SYSTEM")
            .set_user_message("USER")
            .build()
        )
        self.assertLess(prompt.index("SYSTEM"), prompt.index("USER"))

    def test_context_and_tools_included(self):
        """Context snippets and tool outputs should appear in the prompt."""
        prompt = (
            self.PromptBuilder(max_tokens=4096)
            .set_system_instruction("System.")
            .add_context_snippet("Snippet 1")
            .add_context_snippet("Snippet 2")
            .add_tool_output("tool: ok")
            .set_user_message("Question?")
            .build()
        )
        self.assertIn("Snippet 1", prompt)
        self.assertIn("Snippet 2", prompt)
        self.assertIn("tool: ok", prompt)

    def test_empty_builder_raises(self):
        """Building an empty builder should raise ValueError."""
        with self.assertRaises(ValueError):
            self.PromptBuilder(max_tokens=4096).build()

    def test_budget_truncates_context(self):
        """When over budget, context (lowest priority) should be truncated."""
        builder = self.PromptBuilder(max_tokens=30)
        builder.set_system_instruction("System instruction here.")
        builder.set_user_message("User message here.")
        builder.add_context_snippet(" ".join(["context"] * 100))
        prompt = builder.build()
        # System and user must survive; context should be trimmed
        self.assertIn("System instruction here.", prompt)
        self.assertIn("User message here.", prompt)

    def test_budget_truncates_tools_before_system(self):
        """Tools (priority 1) should be truncated before system (priority 0)."""
        builder = self.PromptBuilder(max_tokens=30)
        builder.set_system_instruction("System.")
        builder.add_tool_output(" ".join(["tool"] * 100))
        builder.set_user_message("User.")
        prompt = builder.build()
        self.assertIn("System.", prompt)
        self.assertIn("User.", prompt)

    def test_fluent_chaining(self):
        """Builder methods should return self for fluent chaining."""
        builder = self.PromptBuilder(max_tokens=4096)
        result = builder.set_system_instruction("Sys")
        self.assertIs(result, builder)
        result = builder.set_user_message("Msg")
        self.assertIs(result, builder)
        result = builder.add_context_snippet("Ctx")
        self.assertIs(result, builder)
        result = builder.add_tool_output("Out")
        self.assertIs(result, builder)

    def test_empty_snippets_ignored(self):
        """Empty or whitespace-only snippets should be silently ignored."""
        prompt = (
            self.PromptBuilder(max_tokens=4096)
            .set_system_instruction("Sys")
            .add_context_snippet("")
            .add_context_snippet("   ")
            .set_user_message("Msg")
            .build()
        )
        # Should still build without error
        self.assertIn("Sys", prompt)

    def test_system_before_context_before_tools_before_user(self):
        """Full ordering: system → context → tools → user."""
        prompt = (
            self.PromptBuilder(max_tokens=4096)
            .set_system_instruction("AAA_SYSTEM")
            .add_context_snippet("BBB_CONTEXT")
            .add_tool_output("CCC_TOOLS")
            .set_user_message("DDD_USER")
            .build()
        )
        self.assertLess(prompt.index("AAA_SYSTEM"), prompt.index("BBB_CONTEXT"))
        self.assertLess(prompt.index("BBB_CONTEXT"), prompt.index("CCC_TOOLS"))
        self.assertLess(prompt.index("CCC_TOOLS"), prompt.index("DDD_USER"))

    def test_deterministic_output(self):
        """Same inputs should always produce the same output."""
        def make():
            return (
                self.PromptBuilder(max_tokens=4096)
                .set_system_instruction("Sys")
                .add_context_snippet("Ctx")
                .set_user_message("Msg")
                .build()
            )
        self.assertEqual(make(), make())

    def test_large_budget_no_truncation(self):
        """With a large budget, all content should be preserved verbatim."""
        snippets = [f"snippet {i}" for i in range(5)]
        builder = self.PromptBuilder(max_tokens=100000)
        builder.set_system_instruction("System.")
        for s in snippets:
            builder.add_context_snippet(s)
        builder.set_user_message("User.")
        prompt = builder.build()
        for s in snippets:
            self.assertIn(s, prompt)

    def test_custom_estimator_in_builder(self):
        """Builder should respect a custom token estimator."""
        # Trivial estimator: 1 token per character
        builder = self.PromptBuilder(
            max_tokens=50,
            token_estimator=lambda t: len(t),
        )
        builder.set_system_instruction("Short.")
        builder.add_context_snippet("x" * 200)
        builder.set_user_message("Q?")
        prompt = builder.build()
        # Context should be heavily truncated
        self.assertIn("Short.", prompt)
        self.assertIn("Q?", prompt)
        self.assertLess(len(prompt), 200)

    def test_priority_zero_overflow_raises(self):
        """When priority-0 sections alone exceed the budget, raise ValueError."""
        builder = self.PromptBuilder(max_tokens=2)
        builder.set_system_instruction(" ".join(["word"] * 50))
        builder.set_user_message(" ".join(["word"] * 50))
        with self.assertRaises(ValueError):
            builder.build()


if __name__ == "__main__":
    unittest.main()
