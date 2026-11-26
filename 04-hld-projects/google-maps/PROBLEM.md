# Google Maps & Navigation - Problem Statement

## 1. System to Design
Design the backend infrastructure for a global mapping and navigation system similar to Google Maps. The system must support map tile rendering, real-time telemetry ingestion, dynamic traffic-aware routing, and turn-by-turn navigation.

## 2. Core User Value
Provide users with seamless, fast, and accurate map viewing experiences alongside reliable point-to-point navigation that dynamically adapts to real-world traffic conditions.

## 3. Functional Requirements
- [ ] **FR1:** Map tile rendering across zoom levels (0 to 21).
- [ ] **FR2:** Route planning (fastest/shortest/avoid tolls).
- [ ] **FR3:** Turn-by-turn navigation with dynamic ETA.
- [ ] **FR4:** GPS location telemetry batching from mobile clients.

## 4. Non-Functional Requirements
| Requirement | Target |
|---|---|
| Latency | $< 50\text{ ms}$ for CDN map tile fetch; $< 1\text{ s}$ for initial route calculation |
| Network | Global low-latency map tile CDN |
| Resilience | Resilient navigation during cellular disconnects |
| Availability | High availability ($99.99\%$) |

## 5. Scale & Math
- **Traffic:**
  - $1\text{B MAU}$, $50\text{M}$ concurrent navigation sessions.
  - Client GPS batched every 15–30s.
- **Storage:**
  - Map tile storage: $\approx 100\text{ TB}$ pre-rendered across 21 zoom levels stored in S3 behind CDN edge POPs.
