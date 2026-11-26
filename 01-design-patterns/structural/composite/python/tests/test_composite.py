"""Tests for Composite Pattern implementations."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-variant"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-advanced"))


class TestV1FileSystemComposite(unittest.TestCase):
    """Tests for V1 Basic File System."""

    def test_directory_size_includes_nested_children(self):
        from composite_demo import Directory, File

        root = Directory("root")
        docs = Directory("docs")
        docs.add(File("readme.md", 4))
        docs.add(File("guide.pdf", 16))
        root.add(docs)
        root.add(File("config.yaml", 2))

        self.assertEqual(root.get_size(), 22)


class TestV2GraphicsComposite(unittest.TestCase):
    """Tests for V2 Variant Graphics Groups."""

    def test_group_area_sums_nested_shapes(self):
        from graphics import Circle, GraphicGroup, Rectangle

        icon = GraphicGroup("icon")
        icon.add(Circle("avatar", 0, 0, 2))
        badge = GraphicGroup("badge")
        badge.add(Rectangle("label", 0, 0, 3, 4))
        icon.add(badge)

        self.assertAlmostEqual(icon.area(), 24.57, places=2)

    def test_move_propagates_to_nested_children(self):
        from graphics import Circle, GraphicGroup, Rectangle

        dashboard = GraphicGroup("dashboard")
        chart = Rectangle("chart", 1, 2, 10, 6)
        marker = Circle("marker", 3, 4, 1)
        dashboard.add(chart)
        dashboard.add(marker)

        dashboard.move(5, -2)

        self.assertEqual(chart.position, (6, 0))
        self.assertEqual(marker.position, (8, 2))


class TestV3MenuComposite(unittest.TestCase):
    """Tests for V3 Advanced Menu Hierarchy."""

    def test_menu_counts_items_across_nested_sections(self):
        from menu import Menu, MenuItem

        dinner = Menu("Dinner")
        mains = Menu("Mains")
        desserts = Menu("Desserts")
        mains.add(MenuItem("Paneer Bowl", 12.50, vegetarian=True))
        mains.add(MenuItem("Chicken Bowl", 13.75))
        desserts.add(MenuItem("Kulfi", 5.25, vegetarian=True))
        dinner.add(mains)
        dinner.add(desserts)

        self.assertEqual(dinner.item_count(), 3)
        self.assertAlmostEqual(dinner.total_price(), 31.50, places=2)

    def test_available_items_excludes_sold_out_leaves(self):
        from menu import Menu, MenuItem

        menu = Menu("Cafe")
        menu.add(MenuItem("Coffee", 3.50, vegetarian=True))
        menu.add(MenuItem("Croissant", 4.25, vegetarian=True, available=False))

        self.assertEqual([item.name for item in menu.available_items()], ["Coffee"])


if __name__ == "__main__":
    unittest.main()
