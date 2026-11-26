/**
 * Lightweight tests for realtime channel selection and coordination.
 */
public final class RealtimeDeliveryStrategyTest {
    public static void main(String[] args) {
        RealtimeChannelSelector selector = new RealtimeChannelSelector();
        assert selector.choose(true, true, true) == RealtimeChannelSelector.DeliveryMode.WEBSOCKET;
        assert selector.choose(false, true, true) == RealtimeChannelSelector.DeliveryMode.SSE;
        System.out.println("RealtimeDeliveryStrategyTest passed");
    }
}
