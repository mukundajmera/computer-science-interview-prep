import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import org.junit.jupiter.api.Test;

public class DataPartitionerTest {
    @Test
    void hashPartitionShouldStayWithinBounds() {
        DataPartitioner partitioner = new DataPartitioner(8);
        assertEquals(6, partitioner.hashPartition("user-123"));
        assertEquals(partitioner.hashPartition("user-123"), partitioner.hashPartition("user-123"));
    }

    @Test
    void rangePartitionShouldSelectMatchingRange() {
        DataPartitioner partitioner = new DataPartitioner(3);
        int partition = partitioner.rangePartition(350, List.of(
            new DataPartitioner.IntRange(0, 99),
            new DataPartitioner.IntRange(100, 399),
            new DataPartitioner.IntRange(400, 999)
        ));
        assertEquals(1, partition);
    }

    @Test
    void rangePartitionShouldRejectOverlappingRanges() {
        DataPartitioner partitioner = new DataPartitioner(3);
        assertThrows(IllegalArgumentException.class, () -> partitioner.rangePartition(50, List.of(
            new DataPartitioner.IntRange(0, 99),
            new DataPartitioner.IntRange(50, 199)
        )));
    }
}
