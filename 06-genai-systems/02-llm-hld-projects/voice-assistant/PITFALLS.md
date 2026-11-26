# Real-Time Voice Assistant: Common Pitfalls

Designing real-time voice systems introduces unique challenges not present in text-based chat. From dealing with noisy audio and aggressive VAD models that cut users off, to the complexities of cancelling inflight generations during an interruption, this document covers what can go wrong.

## Section: Latency and Cost Oversights

A major pitfall is improper VAD configuration. If the silence threshold is too short (<300ms), the system cuts users off; if too long (>1000ms), the assistant feels sluggish [Source: UX Research on Conversational Agents]. Another pitfall is ignoring the cost of WebRTC persistent connections and LLM inference, which can escalate quickly to $0.15/minute [Source: LLM API Pricing Tiers]. Additionally, cascading errors—where ASR mistakes (5% WER [Source: Speech Recognition Baselines]) propagate to the LLM and then to TTS—can severely degrade the user experience. Neglecting network jitter and packet loss handling in the WebRTC configuration is also a common oversight that leads to choppy audio.
