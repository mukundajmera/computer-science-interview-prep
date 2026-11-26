import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for Flyweight Pattern implementations.
 */
public class FlyweightTest {
    
    @BeforeEach
    void resetFactories() {
        TreeTypeFactory.reset();
        CharacterStyleFactory.reset();
        IconAssetFactory.reset();
    }
    
    @Test
    @DisplayName("Tree type factory should reuse identical intrinsic state")
    void testTreeTypeFactoryReuse() {
        TreeType oakA = TreeTypeFactory.getTreeType("Oak", "Green", "rough-bark");
        TreeType oakB = TreeTypeFactory.getTreeType("Oak", "Green", "rough-bark");
        TreeType pine = TreeTypeFactory.getTreeType("Pine", "DarkGreen", "needles");
        
        assertSame(oakA, oakB);
        assertNotSame(oakA, pine);
        assertEquals(2, TreeTypeFactory.getTreeTypeCount());
    }
    
    @Test
    @DisplayName("Text document should reuse character styles")
    void testTextDocumentStyleReuse() {
        TextDocument document = new TextDocument();
        
        document.append("Fly", "Inter", 14, "black");
        document.append("weight", "Inter", 14, "black");
        document.append("!", "Inter", 18, "red");
        
        assertEquals(10, document.getGlyphCount());
        assertEquals(2, document.getStyleCount());
        assertEquals(
            "F@(0,0)[Inter/14/black] l@(1,0)[Inter/14/black] " +
            "y@(2,0)[Inter/14/black] w@(3,0)[Inter/14/black] " +
            "e@(4,0)[Inter/14/black] i@(5,0)[Inter/14/black] " +
            "g@(6,0)[Inter/14/black] h@(7,0)[Inter/14/black] " +
            "t@(8,0)[Inter/14/black] !@(9,0)[Inter/18/red]",
            document.renderLine(0)
        );
    }
    
    @Test
    @DisplayName("Toolbar should reuse icon assets while keeping button state extrinsic")
    void testToolbarIconAssetReuse() {
        Toolbar toolbar = new Toolbar();
        
        toolbar.addButton("save", 0, 0, 24, "blue", true);
        toolbar.addButton("save", 32, 0, 32, "gray", false);
        toolbar.addButton("search", 64, 0, 24, "blue", true);
        
        assertEquals(3, toolbar.getButtonCount());
        assertEquals(2, toolbar.getAssetCount());
        assertEquals("save at (0,0), size=24, tint=blue, enabled=true", toolbar.render().get(0));
        assertEquals("save at (32,0), size=32, tint=gray, enabled=false", toolbar.render().get(1));
        assertEquals("search at (64,0), size=24, tint=blue, enabled=true", toolbar.render().get(2));
    }
}
