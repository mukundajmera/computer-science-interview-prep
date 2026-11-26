package chatservice.v3;

import org.junit.jupiter.api.Test;
import java.util.UUID;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ChatServiceV3Test {
    
    @Test
    void testVectorClockHappensBefore() {
        VectorClock clock1 = new VectorClock();
        clock1.increment("us-east");
        
        VectorClock clock2 = new VectorClock(clock1.getClock());
        clock2.increment("us-west");
        
        assertTrue(clock1.happensBefore(clock2));
        assertFalse(clock2.happensBefore(clock1));
    }
    
    @Test
    void testVectorClockConcurrent() {
        VectorClock clock1 = new VectorClock();
        clock1.increment("us-east");
        
        VectorClock clock2 = new VectorClock();
        clock2.increment("us-west");
        
        assertTrue(clock1.isConcurrent(clock2));
        assertTrue(clock2.isConcurrent(clock1));
        assertFalse(clock1.happensBefore(clock2));
        assertFalse(clock2.happensBefore(clock1));
    }
}
