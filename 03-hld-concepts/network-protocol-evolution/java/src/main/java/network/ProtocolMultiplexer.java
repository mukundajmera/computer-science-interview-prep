package network;

import java.util.*;

public class ProtocolMultiplexer {
    private final String mode;
    private final Map<Integer, Frame> tcpBuffer;
    private int tcpExpectedSeq;
    
    private final Map<Integer, Map<Integer, Frame>> quicBuffers;
    private final Map<Integer, Integer> quicExpectedSeqs;
    
    private final List<Frame> processedFrames;

    public ProtocolMultiplexer(String mode) {
        if (!mode.equalsIgnoreCase("TCP") && !mode.equalsIgnoreCase("QUIC")) {
            throw new IllegalArgumentException("Mode must be 'TCP' or 'QUIC'");
        }
        this.mode = mode.toUpperCase();
        this.tcpBuffer = new HashMap<>();
        this.tcpExpectedSeq = 0;
        
        this.quicBuffers = new HashMap<>();
        this.quicExpectedSeqs = new HashMap<>();
        
        this.processedFrames = new ArrayList<>();
    }

    public void receiveFrame(Frame frame) {
        if ("TCP".equals(mode)) {
            handleTcp(frame);
        } else {
            handleQuic(frame);
        }
    }

    private void handleTcp(Frame frame) {
        if (frame.getSequenceNum() == tcpExpectedSeq) {
            processedFrames.add(frame);
            tcpExpectedSeq++;
            
            while (tcpBuffer.containsKey(tcpExpectedSeq)) {
                Frame nextFrame = tcpBuffer.remove(tcpExpectedSeq);
                processedFrames.add(nextFrame);
                tcpExpectedSeq++;
            }
        } else if (frame.getSequenceNum() > tcpExpectedSeq) {
            tcpBuffer.put(frame.getSequenceNum(), frame);
        }
    }

    private void handleQuic(Frame frame) {
        int streamId = frame.getStreamId();
        quicExpectedSeqs.putIfAbsent(streamId, 0);
        quicBuffers.putIfAbsent(streamId, new HashMap<>());
        
        int expectedSeq = quicExpectedSeqs.get(streamId);
        
        if (frame.getSequenceNum() == expectedSeq) {
            processedFrames.add(frame);
            expectedSeq++;
            
            Map<Integer, Frame> buffer = quicBuffers.get(streamId);
            while (buffer.containsKey(expectedSeq)) {
                Frame nextFrame = buffer.remove(expectedSeq);
                processedFrames.add(nextFrame);
                expectedSeq++;
            }
            quicExpectedSeqs.put(streamId, expectedSeq);
        } else if (frame.getSequenceNum() > expectedSeq) {
            quicBuffers.get(streamId).put(frame.getSequenceNum(), frame);
        }
    }

    public List<Frame> getProcessedFrames() {
        return new ArrayList<>(processedFrames);
    }
    
    public Set<Integer> getBlockedStreams() {
        Set<Integer> blocked = new HashSet<>();
        if ("TCP".equals(mode)) {
            if (!tcpBuffer.isEmpty()) {
                for (Frame frame : tcpBuffer.values()) {
                    blocked.add(frame.getStreamId());
                }
            }
        } else {
            for (Map.Entry<Integer, Map<Integer, Frame>> entry : quicBuffers.entrySet()) {
                if (!entry.getValue().isEmpty()) {
                    blocked.add(entry.getKey());
                }
            }
        }
        return blocked;
    }
}
