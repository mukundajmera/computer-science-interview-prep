import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;

/**
 * Tests for Composite Pattern implementations.
 */
public class CompositeTest {

    @Test
    @DisplayName("Directory size should include nested children")
    void testDirectorySizeIncludesNestedChildren() {
        Directory root = new Directory("root");
        Directory docs = new Directory("docs");
        docs.add(new File("readme.md", 4));
        docs.add(new File("guide.pdf", 16));
        root.add(docs);
        root.add(new File("config.yaml", 2));

        assertEquals(22, root.getSize());
    }

    @Test
    @DisplayName("Graphic group area should sum nested shapes")
    void testGraphicGroupArea() {
        GraphicGroup icon = new GraphicGroup("icon");
        icon.add(new Circle("avatar", 0, 0, 2));
        GraphicGroup badge = new GraphicGroup("badge");
        badge.add(new Rectangle("label", 0, 0, 3, 4));
        icon.add(badge);

        assertEquals(24.57, icon.area(), 0.01);
    }

    @Test
    @DisplayName("Graphic group move should propagate to children")
    void testGraphicGroupMove() {
        GraphicGroup dashboard = new GraphicGroup("dashboard");
        Rectangle chart = new Rectangle("chart", 1, 2, 10, 6);
        Circle marker = new Circle("marker", 3, 4, 1);
        dashboard.add(chart);
        dashboard.add(marker);

        dashboard.move(5, -2);

        assertEquals(6, chart.getX());
        assertEquals(0, chart.getY());
        assertEquals(8, marker.getX());
        assertEquals(2, marker.getY());
    }

    @Test
    @DisplayName("Menu should count and price nested items")
    void testMenuCountsAndPricesNestedItems() {
        Menu dinner = new Menu("Dinner");
        Menu mains = new Menu("Mains");
        Menu desserts = new Menu("Desserts");
        mains.add(new MenuItem("Paneer Bowl", 12.50, true));
        mains.add(new MenuItem("Chicken Bowl", 13.75, false));
        desserts.add(new MenuItem("Kulfi", 5.25, true));
        dinner.add(mains);
        dinner.add(desserts);

        assertEquals(3, dinner.itemCount());
        assertEquals(31.50, dinner.totalPrice(), 0.01);
    }

    @Test
    @DisplayName("Menu should exclude sold out leaves from available items")
    void testAvailableItemsExcludeSoldOutLeaves() {
        Menu menu = new Menu("Cafe");
        menu.add(new MenuItem("Coffee", 3.50, true));
        menu.add(new MenuItem("Croissant", 4.25, true, false));

        List<MenuItem> available = menu.availableItems();

        assertEquals(1, available.size());
        assertEquals("Coffee", available.get(0).getName());
    }
}
