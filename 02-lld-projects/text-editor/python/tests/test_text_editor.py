import pytest
import sys
import os

# Add the v1-basic directory to the python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from text_editor import TextEditor

@pytest.fixture
def editor():
    return TextEditor()

def test_insert_and_display(editor):
    editor.insert(1, "First line")
    editor.insert(2, "Second line")
    
    lines = editor.get_all_lines()
    assert len(lines) == 2
    assert lines[0] == "First line"
    assert lines[1] == "Second line"

def test_delete_range(editor):
    editor.insert(1, "L1")
    editor.insert(2, "L2")
    editor.insert(3, "L3")
    editor.insert(4, "L4")

    editor.delete_range(2, 3)
    lines = editor.get_all_lines()
    
    assert len(lines) == 2
    assert lines[0] == "L1"
    assert lines[1] == "L4"

def test_copy_paste(editor):
    editor.insert(1, "A")
    editor.insert(2, "B")
    
    editor.copy(1, 2)
    editor.paste(3)
    
    lines = editor.get_all_lines()
    assert len(lines) == 4
    assert lines[0] == "A"
    assert lines[1] == "B"
    assert lines[2] == "A"
    assert lines[3] == "B"

def test_undo_redo_invalidation(editor):
    editor.insert(1, "One")
    editor.insert(2, "Two")
    
    # Undo "Two"
    editor.undo()
    assert len(editor.get_all_lines()) == 1
    assert editor.get_all_lines()[0] == "One"
    
    # Redo "Two"
    editor.redo()
    assert len(editor.get_all_lines()) == 2
    assert editor.get_all_lines()[1] == "Two"
    
    # Undo "Two" again
    editor.undo()
    
    # Insert new line (should invalidate redo stack)
    editor.insert(2, "Three")
    assert len(editor.get_all_lines()) == 2
    assert editor.get_all_lines()[1] == "Three"
    
    # Redo should do nothing
    editor.redo()
    assert len(editor.get_all_lines()) == 2
    assert editor.get_all_lines()[1] == "Three"
