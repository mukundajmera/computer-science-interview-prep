import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.time.Instant;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class AdClickAggregatorV1Test {

    private AdClickAggregator aggregator;

    @BeforeEach
    public void setUp() {
        aggregator = new AdClickAggregator();
    }

    @Test
    public void testValidIngestAndQuery() {
        Instant time = Instant.parse("2023-10-06T18:45:30Z");

        AdClickAggregator.ClickEvent event = new AdClickAggregator.ClickEvent(
                "evt-1", time, "camp-1", "adgroup-1", "pub-1"
        );

        aggregator.processEvent(event);

        // 1m window
        assertEquals(1L, aggregator.getCount("campaign", "camp-1", "1m", "2023-10-06T18:45"));
        assertEquals(1L, aggregator.getCount("adGroup", "adgroup-1", "1m", "2023-10-06T18:45"));
        assertEquals(1L, aggregator.getCount("publisher", "pub-1", "1m", "2023-10-06T18:45"));

        // 1h window
        assertEquals(1L, aggregator.getCount("campaign", "camp-1", "1h", "2023-10-06T18"));

        // 1d window
        assertEquals(1L, aggregator.getCount("campaign", "camp-1", "1d", "2023-10-06"));

        // Empty query
        assertEquals(0L, aggregator.getCount("campaign", "camp-2", "1m", "2023-10-06T18:45"));
    }

    @Test
    public void testDuplicateDelivery() {
        Instant time = Instant.parse("2023-10-06T18:45:30Z");

        AdClickAggregator.ClickEvent event1 = new AdClickAggregator.ClickEvent(
                "evt-1", time, "camp-1", "adgroup-1", "pub-1"
        );
        AdClickAggregator.ClickEvent event2 = new AdClickAggregator.ClickEvent(
                "evt-1", time, "camp-1", "adgroup-1", "pub-1"
        );

        aggregator.processEvent(event1);
        aggregator.processEvent(event2); // Duplicate id

        assertEquals(1L, aggregator.getCount("campaign", "camp-1", "1m", "2023-10-06T18:45"));
    }

    @Test
    public void testWindowBoundariesAndDimensionSeparation() {
        Instant time1 = Instant.parse("2023-10-06T18:45:30Z");
        Instant time2 = Instant.parse("2023-10-06T18:46:10Z"); // Next minute

        AdClickAggregator.ClickEvent event1 = new AdClickAggregator.ClickEvent(
                "evt-1", time1, "camp-1", "adgroup-1", "pub-1"
        );
        AdClickAggregator.ClickEvent event2 = new AdClickAggregator.ClickEvent(
                "evt-2", time2, "camp-2", "adgroup-1", "pub-2"
        );

        aggregator.processEvent(event1);
        aggregator.processEvent(event2);

        // Different minutes
        assertEquals(1L, aggregator.getCount("campaign", "camp-1", "1m", "2023-10-06T18:45"));
        assertEquals(0L, aggregator.getCount("campaign", "camp-1", "1m", "2023-10-06T18:46"));

        assertEquals(0L, aggregator.getCount("campaign", "camp-2", "1m", "2023-10-06T18:45"));
        assertEquals(1L, aggregator.getCount("campaign", "camp-2", "1m", "2023-10-06T18:46"));

        // Same hour, same adGroup
        assertEquals(2L, aggregator.getCount("adGroup", "adgroup-1", "1h", "2023-10-06T18"));
    }

    @Test
    public void testInvalidInput() {
        Instant time = Instant.parse("2023-10-06T18:45:30Z");

        // Null eventId
        assertThrows(IllegalArgumentException.class, () -> {
            new AdClickAggregator.ClickEvent(null, time, "camp-1", "adgroup-1", "pub-1");
        });

        // Empty eventId
        assertThrows(IllegalArgumentException.class, () -> {
            new AdClickAggregator.ClickEvent("", time, "camp-1", "adgroup-1", "pub-1");
        });

        // Null time
        assertThrows(IllegalArgumentException.class, () -> {
            new AdClickAggregator.ClickEvent("evt-1", null, "camp-1", "adgroup-1", "pub-1");
        });

        // Null event processed
        assertThrows(IllegalArgumentException.class, () -> {
            aggregator.processEvent(null);
        });
    }
}
