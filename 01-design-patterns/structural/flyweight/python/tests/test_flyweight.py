"""Tests for Flyweight Pattern implementations."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-variant"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-advanced"))


class TestV1TreeForest(unittest.TestCase):
    """Tests for V1 Basic tree flyweights."""

    def test_factory_reuses_tree_type_for_same_intrinsic_state(self):
        from flyweight_demo import TreeTypeFactory

        TreeTypeFactory.reset()

        oak_a = TreeTypeFactory.get_tree_type("Oak", "Green", "rough-bark")
        oak_b = TreeTypeFactory.get_tree_type("Oak", "Green", "rough-bark")
        pine = TreeTypeFactory.get_tree_type("Pine", "DarkGreen", "needles")

        self.assertIs(oak_a, oak_b)
        self.assertIsNot(oak_a, pine)
        self.assertEqual(TreeTypeFactory.get_type_count(), 2)


class TestV2TextEditor(unittest.TestCase):
    """Tests for V2 text-editor flyweights."""

    def test_document_reuses_character_style_across_many_glyphs(self):
        from text_editor import TextDocument

        document = TextDocument()

        document.append("Fly", "Inter", 14, "black")
        document.append("weight", "Inter", 14, "black")
        document.append("!", "Inter", 18, "red")

        self.assertEqual(document.glyph_count, 10)
        self.assertEqual(document.style_count, 2)
        self.assertEqual(
            document.render_line(0),
            "F@(0,0)[Inter/14/black] l@(1,0)[Inter/14/black] "
            "y@(2,0)[Inter/14/black] w@(3,0)[Inter/14/black] "
            "e@(4,0)[Inter/14/black] i@(5,0)[Inter/14/black] "
            "g@(6,0)[Inter/14/black] h@(7,0)[Inter/14/black] "
            "t@(8,0)[Inter/14/black] !@(9,0)[Inter/18/red]",
        )


class TestV3IconSystem(unittest.TestCase):
    """Tests for V3 icon resource flyweights."""

    def test_toolbar_reuses_icon_assets_with_extrinsic_button_state(self):
        from icon_system import Toolbar

        toolbar = Toolbar()

        toolbar.add_button("save", 0, 0, 24, "blue", True)
        toolbar.add_button("save", 32, 0, 32, "gray", False)
        toolbar.add_button("search", 64, 0, 24, "blue", True)

        self.assertEqual(toolbar.button_count, 3)
        self.assertEqual(toolbar.asset_count, 2)
        self.assertEqual(
            toolbar.render(),
            [
                "save at (0,0), size=24, tint=blue, enabled=true",
                "save at (32,0), size=32, tint=gray, enabled=false",
                "search at (64,0), size=24, tint=blue, enabled=true",
            ],
        )


if __name__ == "__main__":
    unittest.main()
