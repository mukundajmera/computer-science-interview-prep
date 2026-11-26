import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

public class CapSystemTest {
    @Test
    void cpShouldRejectReadDuringPartition() {
        CapSystem system = new CapSystem(CapSystem.Mode.CP);
        assertEquals("REJECTED_FOR_CONSISTENCY", system.readDuringPartition());
    }

    @Test
    void apShouldAllowStaleReadDuringPartition() {
        CapSystem system = new CapSystem(CapSystem.Mode.AP);
        assertEquals("STALE_OK", system.readDuringPartition());
    }

    @Test
    void shouldRejectMissingMode() {
        assertThrows(IllegalArgumentException.class, () -> new CapSystem(null));
    }
}
