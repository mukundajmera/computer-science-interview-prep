package network;

public class Frame {
    private final int streamId;
    private final String frameType;
    private final int flags;
    private final String payload;
    private final int sequenceNum;

    public Frame(int streamId, String frameType, int flags, String payload, int sequenceNum) {
        this.streamId = streamId;
        this.frameType = frameType;
        this.flags = flags;
        this.payload = payload;
        this.sequenceNum = sequenceNum;
    }

    public int getStreamId() {
        return streamId;
    }

    public String getFrameType() {
        return frameType;
    }

    public int getFlags() {
        return flags;
    }

    public String getPayload() {
        return payload;
    }

    public int getSequenceNum() {
        return sequenceNum;
    }
}
