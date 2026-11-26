# Pitfalls and Failure Traces

## 1. Non-Deterministic Rollouts (Simulation / Proof Sketch)
- **Failure Trace**: If the rollout uses `Math.random()` or a timestamp-based hash rather than a stable hash of `userId` and `flagKey`.
- **Assumption**: The server does not store every user's evaluated rollout persistently, instead recalculating dynamically.
- **Trace**: 
  1. User `u123` requests `experiment_X` config.
  2. Engine calls `random()`, returning bucket `30` (Variant A).
  3. User `u123` refreshes the app.
  4. Engine calls `random()`, returning bucket `85` (Variant B).
  5. The user's experience flickers drastically across requests.

## 2. Blocking Listeners causing Thread Starvation
- **Failure Trace**: Synchronous listeners performing long-running I/O when `updateFlag` is invoked.
- **Assumption**: Notification loops exist on the thread processing configuration updates.
- **Trace**: 
  1. A background thread processes an incoming config update from a central DB.
  2. The thread updates the `ConcurrentHashMap`.
  3. The thread calls `listener.onFlagUpdated()` directly.
  4. The listener makes a 5-second blocking HTTP call to an external service.
  5. If updates happen 10x per second, the update thread blocks indefinitely, stopping all subsequent feature flag propagations.

## 3. Lock Contention on Read/Write
- **Failure Trace**: Global synchronization on evaluation paths.
- **Assumption**: Heavy read workload (e.g., every HTTP request triggers 10 evaluations).
- **Trace**: 
  1. `evaluate()` and `update_flag()` share a standard `threading.Lock()` or `synchronized` block.
  2. A minor config update acquires the lock.
  3. 1,000 concurrent evaluation requests queue up, spiking system latency.

## 4. Unhandled Missing Attributes
- **Failure Trace**: Missing fallback logic when segments expect data the user doesn't have.
- **Assumption**: Rule execution throws instead of safely skipping if `context.getAttribute("country")` is null.
- **Trace**: 
  1. Rule checks `country == "US"`.
  2. The `UserContext` does not have a `country` key.
  3. Code hits `NullPointerException` (Java) or unhandled `KeyError` (Python).
  4. Evaluation fails completely rather than returning the `defaultVariant`.
