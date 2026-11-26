"""v1-simple: choose realtime delivery mode from simple requirements."""

from enum import Enum


class DeliveryMode(str, Enum):
    POLLING = "polling"
    LONG_POLLING = "long_polling"
    SSE = "sse"
    WEBSOCKET = "websocket"
    WEBRTC = "webrtc"


class RealtimeChannelSelector:
    def choose(self, bidirectional: bool, strict_low_latency: bool, browser_only_client: bool) -> DeliveryMode:
        if bidirectional:
            return DeliveryMode.WEBSOCKET
        if strict_low_latency and browser_only_client:
            return DeliveryMode.SSE
        if strict_low_latency:
            return DeliveryMode.LONG_POLLING
        return DeliveryMode.POLLING
