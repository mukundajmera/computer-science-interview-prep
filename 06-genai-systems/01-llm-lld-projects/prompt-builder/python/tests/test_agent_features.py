import sys
import os
import pytest

# Insert v2-extended into sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from template import PromptTemplate, TemplateVariable
from few_shot_selector import FewShotExample, FewShotFormatter
from prompt_builder import ChatPromptBuilder

def test_template_variable_type_validation_success():
    """Test successful type validation for template variables."""
    variables = [
        TemplateVariable(name="count", expected_type=int),
        TemplateVariable(name="name", expected_type=str)
    ]
    tpl = PromptTemplate("Count is {count} and name is {name}.", variables=variables)
    result = tpl.render({"count": 5, "name": "Alice"})
    assert result == "Count is 5 and name is Alice."

def test_template_variable_type_validation_failure():
    """Test type validation failure for template variables."""
    variables = [
        TemplateVariable(name="count", expected_type=int)
    ]
    tpl = PromptTemplate("Count is {count}.", variables=variables)
    with pytest.raises(TypeError) as exc:
        tpl.render({"count": "five"})
    assert "Variable 'count' expected type <class 'int'>, got <class 'str'>" in str(exc.value)

def test_few_shot_formatter_string_creation():
    """Test formatting of few-shot examples."""
    examples = [
        FewShotExample(query="hi", response="hello"),
        FewShotExample(query="bye", response="goodbye")
    ]
    formatter = FewShotFormatter("Q: {query}\nA: {response}")
    result = formatter.format(examples)
    expected = "Q: hi\nA: hello\n\nQ: bye\nA: goodbye"
    assert result == expected

def test_chat_prompt_builder_basic_formatting():
    """Test basic ChatPromptBuilder formatting."""
    builder = ChatPromptBuilder(max_tokens=100)
    builder.set_system_message("You are an assistant.")
    builder.add_user_message("Hello!")
    builder.add_assistant_message("Hi there!")
    builder.add_user_message("How are you?")
    
    result = builder.build()
    
    assert len(result) == 4
    assert result[0] == {"role": "system", "content": "You are an assistant."}
    assert result[1] == {"role": "user", "content": "Hello!"}
    assert result[2] == {"role": "assistant", "content": "Hi there!"}
    assert result[3] == {"role": "user", "content": "How are you?"}

def test_chat_prompt_builder_truncation_guard():
    """Test that ChatPromptBuilder applies truncation guard based on priority."""
    builder = ChatPromptBuilder(max_tokens=30)
    
    # Priority 0 is kept
    builder.set_system_message("System instruction here.")
    builder.add_user_message("User message here.")
    
    # Priority 2 is truncated
    long_assistant_msg = " ".join(["assistant"] * 100)
    builder.add_assistant_message(long_assistant_msg, priority=2)
    
    result = builder.build()
    
    # Length should be 3
    assert len(result) == 3
    
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System instruction here."
    
    assert result[1]["role"] == "user"
    assert result[1]["content"] == "User message here."
    
    assert result[2]["role"] == "assistant"
    # Should be truncated
    assert len(result[2]["content"]) < len(long_assistant_msg)
    
def test_chat_prompt_builder_truncation_removes_empty():
    """Test that fully truncated messages are removed."""
    builder = ChatPromptBuilder(max_tokens=4)
    
    builder.set_system_message("System test message.")
    
    # Priority 2 will be completely truncated because budget is small
    long_assistant_msg = " ".join(["assistant"] * 100)
    builder.add_assistant_message(long_assistant_msg, priority=2)
    
    result = builder.build()
    
    # Only the system message should be kept
    assert len(result) == 1
    assert result[0]["role"] == "system"

