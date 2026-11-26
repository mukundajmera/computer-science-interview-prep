"""Command pattern tests backed by the example source files."""
import importlib.util
from pathlib import Path
import unittest


PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


text_editor = load_module("text_editor", "python/v2-variant/text_editor.py")
macro_commands = load_module("macro_commands", "python/v3-advanced/macro_commands.py")


class TestCommandPattern(unittest.TestCase):
    def test_text_editor_commands_support_undo_and_redo(self):
        """Editor commands encapsulate reversible text changes."""
        editor = text_editor.TextEditor()
        history = text_editor.CommandHistory()

        history.execute(text_editor.InsertTextCommand(editor, "hello"))
        history.execute(text_editor.InsertTextCommand(editor, " world"))
        history.execute(text_editor.DeleteTextCommand(editor, 5, 6))

        self.assertEqual(editor.content, "hello")
        history.undo()
        self.assertEqual(editor.content, "hello world")
        history.undo()
        self.assertEqual(editor.content, "hello")
        history.redo()
        self.assertEqual(editor.content, "hello world")

    def test_macro_command_executes_and_undoes_in_reverse_order(self):
        """A macro command behaves like one reversible command."""
        document = macro_commands.TextDocument()
        macro = macro_commands.MacroCommand(
            "publish draft",
            [
                macro_commands.AppendLineCommand(document, "title"),
                macro_commands.AppendLineCommand(document, "body"),
                macro_commands.ReplaceTextCommand(document, "body", "final body"),
            ],
        )

        macro.execute()
        self.assertEqual(document.content, "title\nfinal body")

        macro.undo()
        self.assertEqual(document.content, "")

    def test_macro_command_rolls_back_completed_steps_on_failure(self):
        """Failed macros undo already-completed commands."""
        document = macro_commands.TextDocument()
        macro = macro_commands.MacroCommand(
            "unsafe publish",
            [
                macro_commands.AppendLineCommand(document, "draft"),
                macro_commands.FailingCommand("storage unavailable"),
            ],
        )

        with self.assertRaises(RuntimeError):
            macro.execute()

        self.assertEqual(document.content, "")


if __name__ == "__main__":
    unittest.main()
