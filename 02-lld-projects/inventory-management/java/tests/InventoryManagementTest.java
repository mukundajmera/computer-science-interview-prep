import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class InventoryManagementTest {

    @Test
    void basicStockMutationAndTransfer() {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addWarehouse("W2");

        manager.addStock("W1", "SKU", 10);
        assertTrue(manager.removeStock("W1", "SKU", 3));
        assertTrue(manager.transferStock("W1", "W2", "SKU", 4));

        assertEquals(2, manager.checkAvailability("SKU", 3).size());
    }

    @Test
    void rejectsOverRemoval() {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addStock("W1", "SKU", 2);

        assertFalse(manager.removeStock("W1", "SKU", 5));
    }
}
