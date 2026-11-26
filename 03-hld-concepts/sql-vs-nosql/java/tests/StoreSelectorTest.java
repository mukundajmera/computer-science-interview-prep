import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class StoreSelectorTest {
    @Test
    void shouldPreferSqlForTransactions() {
        StoreSelector selector = new StoreSelector();
        String store = selector.chooseStore(new StoreSelector.Workload(true, false, false, false));
        assertEquals("SQL", store);
    }

    @Test
    void shouldPreferNoSqlForScale() {
        StoreSelector selector = new StoreSelector();
        String store = selector.chooseStore(new StoreSelector.Workload(false, false, false, true));
        assertEquals("NoSQL", store);
    }
}
