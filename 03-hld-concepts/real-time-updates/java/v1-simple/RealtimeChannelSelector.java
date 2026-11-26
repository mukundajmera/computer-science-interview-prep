import java.util.EnumSet;
import java.util.Set;

/**
 * v1-simple: Choose a delivery mode from basic requirements.
 */
public final class RealtimeChannelSelector {
    public enum DeliveryMode {
        POLLING,
        LONG_POLLING,
        SSE,
        WEBSOCKET,
        WEBRTC
    }

    public DeliveryMode choose(boolean bidirectional, boolean strictLowLatency, boolean browserOnlyClient) {
        if (bidirectional) {
            return strictLowLatency ? DeliveryMode.WEBSOCKET : DeliveryMode.WEBSOCKET;
        }
        if (strictLowLatency && browserOnlyClient) {
            return DeliveryMode.SSE;
        }
        return strictLowLatency ? DeliveryMode.LONG_POLLING : DeliveryMode.POLLING;
    }

    public Set<DeliveryMode> supportedModes() {
        return EnumSet.allOf(DeliveryMode.class);
    }
}
