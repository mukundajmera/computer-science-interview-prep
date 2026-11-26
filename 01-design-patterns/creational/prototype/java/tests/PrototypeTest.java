import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import prototype.v1.Circle;
import prototype.v1.Rectangle;
import prototype.v1.Document;
import prototype.v1.Shape;
import prototype.v1.PrototypeRegistry;
import prototype.v1.Circle;
import prototype.v1.Rectangle;
import prototype.v1.Document;
import prototype.v1.Shape;
import prototype.v1.PrototypeRegistry;
import prototype.v1.*;
import prototype.v2.GameUnitPrototypeDemo.*;
import prototype.v3.ConfigSnapshotManagerDemo.*;

public class PrototypeTest {

    @Test
    @DisplayName("Shape cloning produces independent instances with identical state")
    void testShapeCloningProducesIndependentObjects() {
        Circle originalCircle = new Circle();
        originalCircle.setRadius(25).setColor("red").setPosition(10, 20);

        Circle clonedCircle = originalCircle.clone();
        assertNotSame(originalCircle, clonedCircle);
        assertEquals(originalCircle.toString(), clonedCircle.toString());

        clonedCircle.setPosition(50, 60);
        assertNotEquals(originalCircle.toString(), clonedCircle.toString());

        Rectangle originalRect = new Rectangle();
        originalRect.setDimensions(30, 40).setColor("blue");
        Rectangle clonedRect = originalRect.clone();
        assertNotSame(originalRect, clonedRect);
        assertEquals(originalRect.toString(), clonedRect.toString());
    }

    @Test
    @DisplayName("Document clone performs deep copy on collections")
    void testDocumentDeepCopyIndependence() {
        Document originalDoc = new Document();
        originalDoc.setTitle("Spec")
                .setContent("Initial content")
                .addTag("draft")
                .addMetadata("author", "Alice");

        Document clonedDoc = originalDoc.clone();
        assertNotSame(originalDoc, clonedDoc);

        clonedDoc.setTitle("Final Spec")
                .addTag("reviewed")
                .addMetadata("reviewer", "Bob");

        assertFalse(originalDoc.toString().contains("reviewed"));
        assertFalse(originalDoc.toString().contains("Bob"));
        assertTrue(clonedDoc.toString().contains("reviewed"));
    }

    @Test
    @DisplayName("PrototypeRegistry registers and returns clones, throwing on missing key")
    void testPrototypeRegistryLookupAndMissingKey() {
        Circle protoCircle = new Circle();
        protoCircle.setRadius(5).setColor("green");
        PrototypeRegistry.register("green-circle-test", protoCircle);

        assertTrue(PrototypeRegistry.contains("green-circle-test"));
        Shape clone = (Shape) PrototypeRegistry.getClone("green-circle-test");
        assertNotNull(clone);
        assertNotSame(protoCircle, clone);

        assertThrows(IllegalArgumentException.class, () -> PrototypeRegistry.getClone("non-existent-key"));
    }

    @Test
    @DisplayName("v2 UnitSpawnerRegistry spawns independent units with deep-copied abilities")
    void testGameUnitSpawner() {
        UnitSpawnerRegistry registry = new UnitSpawnerRegistry();
        Warrior warrior = new Warrior("Paladin", 140, List.of("HolyLight", "Smite"));
        registry.registerPrototype("paladin", warrior);

        GameUnit unit1 = registry.spawn("paladin");
        GameUnit unit2 = registry.spawn("paladin");
        assertNotSame(unit1, unit2);
        assertNotSame(unit1, warrior);

        assertEquals(140, unit1.getHealth());
        unit1.takeDamage(50);
        assertEquals(90, unit1.getHealth());
        assertEquals(140, unit2.getHealth());

        unit1.addAbility("ShieldWall");
        assertTrue(unit1.getAbilities().contains("ShieldWall"));
        assertFalse(unit2.getAbilities().contains("ShieldWall"));

        assertThrows(IllegalArgumentException.class, () -> registry.spawn("unknown_unit"));
    }

    @Test
    @DisplayName("v3 ConfigurationManager commit and rollback using prototype snapshot drafts")
    void testConfigurationSnapshotRollback() {
        ConfigurationManager manager = new ConfigurationManager(
                Map.of("host", "127.0.0.1", "port", "8080"),
                Map.of("max_retries", 3)
        );

        assertEquals(1, manager.getCurrent().getVersion());
        assertEquals("127.0.0.1", manager.getCurrent().getProperty("host"));

        manager.commitUpdate(draft -> {
            draft.setProperty("host", "10.0.0.1");
            draft.setLimit("max_retries", 5);
        });

        assertEquals(2, manager.getCurrent().getVersion());
        assertEquals("10.0.0.1", manager.getCurrent().getProperty("host"));
        assertEquals(5, manager.getCurrent().getLimit("max_retries"));
        assertEquals(1, manager.getHistoryDepth());

        assertTrue(manager.rollback());
        assertEquals(1, manager.getCurrent().getVersion());
        assertEquals("127.0.0.1", manager.getCurrent().getProperty("host"));
        assertEquals(3, manager.getCurrent().getLimit("max_retries"));

        assertFalse(manager.rollback());
    }
}
