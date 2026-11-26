package network;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Set;

public class ProtocolMultiplexerTest {

    @Test
    public void testTcpInOrder() {
        ProtocolMultiplexer mux = new ProtocolMultiplexer("TCP");
        Frame f1 = new Frame(1, "DATA", 0, "payload1", 0);
        Frame f2 = new Frame(2, "DATA", 0, "payload2", 1);
        
        mux.receiveFrame(f1);
        mux.receiveFrame(f2);
        
        List<Frame> processed = mux.getProcessedFrames();
        assertEquals(2, processed.size());
        assertEquals(f1, processed.get(0));
        assertEquals(f2, processed.get(1));
        assertTrue(mux.getBlockedStreams().isEmpty());
    }

    @Test
    public void testTcpHolBlocking() {
        ProtocolMultiplexer mux = new ProtocolMultiplexer("TCP");
        Frame f1 = new Frame(1, "DATA", 0, "payload1", 0);
        // Frame sequence 1 dropped
        Frame f3 = new Frame(2, "DATA", 0, "payload3", 2);
        
        mux.receiveFrame(f1);
        mux.receiveFrame(f3);
        
        List<Frame> processed = mux.getProcessedFrames();
        assertEquals(1, processed.size());
        assertEquals(f1, processed.get(0));
        
        Set<Integer> blocked = mux.getBlockedStreams();
        assertTrue(blocked.contains(2));
        
        Frame f2 = new Frame(1, "DATA", 0, "payload2", 1);
        mux.receiveFrame(f2);
        
        processed = mux.getProcessedFrames();
        assertEquals(3, processed.size());
        assertEquals(f2, processed.get(1));
        assertEquals(f3, processed.get(2));
        assertTrue(mux.getBlockedStreams().isEmpty());
    }

    @Test
    public void testQuicIndependentStreams() {
        ProtocolMultiplexer mux = new ProtocolMultiplexer("QUIC");
        Frame f1 = new Frame(1, "DATA", 0, "s1p1", 0);
        // Stream 1 missing sequence 1
        Frame f3 = new Frame(2, "DATA", 0, "s2p1", 0);
        Frame f4 = new Frame(2, "DATA", 0, "s2p2", 1);
        
        mux.receiveFrame(f1);
        mux.receiveFrame(f3);
        mux.receiveFrame(f4);
        
        List<Frame> processed = mux.getProcessedFrames();
        assertEquals(3, processed.size());
        assertEquals(f1, processed.get(0));
        assertEquals(f3, processed.get(1));
        assertEquals(f4, processed.get(2));
        
        Frame f5 = new Frame(1, "DATA", 0, "s1p3", 2);
        mux.receiveFrame(f5);
        
        assertEquals(3, mux.getProcessedFrames().size());
        
        Set<Integer> blocked = mux.getBlockedStreams();
        assertTrue(blocked.contains(1));
        assertFalse(blocked.contains(2));
        
        Frame f2 = new Frame(1, "DATA", 0, "s1p2", 1);
        mux.receiveFrame(f2);
        
        assertEquals(5, mux.getProcessedFrames().size());
        assertTrue(mux.getBlockedStreams().isEmpty());
    }

    @Test
    public void testInvalidMode() {
        assertThrows(IllegalArgumentException.class, () -> {
            new ProtocolMultiplexer("UDP");
        });
    }
}
