import sys
import os
import pytest

# Insert v2-extended path FIRST
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
for module_name in ["text_editor", "commands", "text_buffer", "history_manager", "clipboard"]:
    sys.modules.pop(module_name, None)

from text_editor import TextEditor
from commands import MacroCommand

def test_v2_insert_and_delete():
    editor = TextEditor()
    editor.insert(1, "Hello")
    editor.insert(2, "World")
    assert editor.get_all_lines() == ["Hello", "World"]
    editor.delete(1)
    assert editor.get_all_lines() == ["World"]

def test_v2_undo_redo():
    editor = TextEditor()
    editor.insert(1, "Line 1")
    editor.insert(2, "Line 2")
    assert editor.get_all_lines() == ["Line 1", "Line 2"]
    
    editor.undo()
    assert editor.get_all_lines() == ["Line 1"]
    
    editor.redo()
    assert editor.get_all_lines() == ["Line 1", "Line 2"]
    
    editor.delete(1)
    assert editor.get_all_lines() == ["Line 2"]
    editor.undo()
    assert editor.get_all_lines() == ["Line 1", "Line 2"]

def test_v2_macro_recording():
    editor = TextEditor()
    editor.insert(1, "Initial")
    
    editor.start_macro()
    editor.insert(2, "Macro 1")
    editor.insert(3, "Macro 2")
    macro = editor.stop_macro()
    
    assert editor.get_all_lines() == ["Initial", "Macro 1", "Macro 2"]
    
    editor.undo() # Should undo the entire macro
    assert editor.get_all_lines() == ["Initial"]
    
    editor.execute_macro(macro)
    assert editor.get_all_lines() == ["Initial", "Macro 1", "Macro 2"]
    
def test_v2_history_limit():
    editor = TextEditor(history_limit=2)
    editor.insert(1, "Line 1")
    editor.insert(2, "Line 2")
    editor.insert(3, "Line 3")
    
    # We have 3 inserts, but limit is 2. So we can only undo twice.
    editor.undo()
    editor.undo()
    # The first insert should be un-undoable
    editor.undo() 
    assert editor.get_all_lines() == ["Line 1"]

def test_v2_replace():
    editor = TextEditor()
    editor.insert(1, "Old Text")
    editor.replace(1, "New Text")
    assert editor.get_all_lines() == ["New Text"]
    
    editor.undo()
    assert editor.get_all_lines() == ["Old Text"]
