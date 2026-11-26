# Real-Time Voice Assistant: System Design

This document details the chosen architecture for the voice assistant. It outlines the WebRTC signaling flow, the integration of Voice Activity Detection (VAD) algorithms, the orchestration of the AI pipeline, and the sequence of events during a user barge-in.

## 1. 📝 Requirements Clarification

### Functional Requirements
- Real-time conversational interface with voice input/output
- Low-latency response times
- Barge-in capabilities (user can interrupt the assistant)

### Non-Functional Requirements
- High availability (99.9%)
- Strict latency limits (TTFA < 500ms)
- Scalability to handle high concurrent sessions

### GenAI-Specific Requirements
- Fast LLM inference with streaming text output
- High-quality streaming TTS synthesis
- Robust VAD for accurate endpointing

## 2. 📊 Back-of-Envelope Estimation

- Target Latency: < 500ms TTFA
- Concurrent Sessions: 10,000
- Audio Bitrate: 32 kbps (Opus)
- Network Bandwidth: ~320 Mbps

## 3. 🏗️ Architecture Design

See the diagrams directory for detailed Mermaid visualizations.

### Latency Budget Table

| Component | Target Latency | Notes |
| :--- | :--- | :--- |
| Network RTT | 50ms | Optimized via Edge PoPs |
| VAD / Endpointing | 50ms | Includes 500ms silence threshold |
| ASR Processing | 100ms | Streaming chunk processing |
| LLM TTFT | 150ms | Time to first text token |
| TTS Synthesis | 150ms | First audio chunk generation |
| **Total TTFA** | **500ms** | End-to-end user perceived latency |

## Section: Gateway Architecture

The design centers around a WebRTC gateway deployed at edge PoPs. This gateway handles media negotiation and forwards audio streams to a centralized processing cluster via gRPC. The processing cluster orchestrates the ASR, LLM, and TTS services. We employ an event-driven architecture to manage asynchronous tasks such as user barge-in. State is maintained in a fast in-memory store like Redis (sub-millisecond latency [Source: Redis Documentation]) to track session contexts, enabling seamless conversation flow even if underlying microservices scale dynamically up to 1,000 nodes [Source: K8s Autoscaling Benchmarks].
