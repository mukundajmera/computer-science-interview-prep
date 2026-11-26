"""Tests for the Memento pattern v2/v3 text editor examples."""
import importlib.util
from pathlib import Path
from types import ModuleType
import unittest


PYTHON_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, PYTHON_DIR / relative_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestMementoPattern(unittest.TestCase):
    def test_v2_bounded_history_keeps_recent_labeled_snapshots(self) -> None:
        v2 = load_module("memento_v2", "v2-variant/memento_demo.py")
        editor = v2.TextEditor()
        history = v2.BoundedHistory(max_snapshots=3)

        history.push(editor.save("empty"))
        editor.type("Hello")
        history.push(editor.save("greeting"))
        editor.type(" World")
        history.push(editor.save("subject"))
        editor.delete()
        history.push(editor.save("trimmed"))

        self.assertEqual(["greeting", "subject", "trimmed"], history.labels())

        editor.restore(history.undo())
        self.assertEqual("Hello World", editor.content)
        editor.restore(history.undo())
        self.assertEqual("Hello", editor.content)
        editor.restore(history.undo())
        self.assertEqual("Hello", editor.content)

        editor.restore(history.redo())
        self.assertEqual("Hello World", editor.content)

    def test_v3_transactions_rollback_commit_and_restore_checkpoints(self) -> None:
        v3 = load_module("memento_v3", "v3-advanced/memento_demo.py")
        editor = v3.TransactionalTextEditor()
        history = v3.CheckpointHistory(editor)

        history.snapshot("empty")
        editor.type("Draft")
        history.snapshot("draft")
        history.save_checkpoint("approved-draft")

        history.begin_transaction("risky rewrite")
        editor.type(" unsafe")
        history.rollback_transaction()
        self.assertEqual("Draft", editor.content)

        history.begin_transaction("publish edit")
        editor.type(" v2")
        history.commit_transaction("published")
        self.assertEqual("Draft v2", editor.content)

        history.undo()
        self.assertEqual("Draft", editor.content)
        history.redo()
        self.assertEqual("Draft v2", editor.content)

        history.restore_checkpoint("approved-draft")
        self.assertEqual("Draft", editor.content)


if __name__ == "__main__":
    unittest.main()
