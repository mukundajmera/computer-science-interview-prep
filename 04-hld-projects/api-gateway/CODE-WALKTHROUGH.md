# API Gateway Simulation Walkthrough

This document maps the concepts from the HLD (`DESIGN.md`) directly to the implementation in the bounded simulators.

## Scope of Simulation
The code provided focuses on the **Filter Chain Model** of the API Gateway, particularly:
1. **Security/Auth Filter**: Basic validation that an `Authorization` header is present.
2. **Circuit Breaker Filter**: Validating if downstream communication is allowed based on the `CircuitBreaker` state (CLOSED vs. OPEN).

To keep the simulation focused and avoid massive complexity:
* **Transport Simplification**: HTTP/2 multiplexing, connections, and parsing are mocked out. We assume standard in-memory structures like `Request` and `Response`.
* **Security Simplification**: We mock out complete JWT verification and JWKS retrieval for a simpler `Authorization` header check.
* **Consistency/Storage Simplification**: The token-bucket rate limiting via Redis is omitted to keep it standard-library bounded. We only simulate the resilience filter layer.
* **Clock Simplification**: The circuit breaker omits the time-based transition from OPEN to HALF-OPEN, instead relying on manual tripping or reset methods for test determinism.

## Filter Execution

The main component is `ApiGatewaySimulator`, which sequentially executes filters (simulated directly in the `handleRequest` method). 

### 1. Normal Trace
- The client sends a valid request (has an `Authorization` header).
- The `CircuitBreaker` allows the request (it is in `CLOSED` state).
- The proxy logic (mocked) forwards the request to downstream.
- A 200 OK response is simulated and returned.

### 2. Failure Trace (Circuit Breaker)
- If the downstream service is failing continuously, the `CircuitBreaker` trips to the `OPEN` state.
- Subsequent client requests hit the gateway.
- The **Circuit Breaker Filter** blocks the request and sheds traffic by returning a fast-fail `503 Service Unavailable` response.
- The mock ensures that in this state, no requests proceed to downstream proxies until the breaker is reset or transitions to `HALF-OPEN` (which can be extended in v2).

## Language Parity
- **Java**: Models (`Request`, `Response`, `CircuitBreaker`) and Simulator are implemented in `java/v1-basic/`. Test execution happens via a direct `main` method in `tests/ApiGatewaySimulatorTest.java`.
- **Python**: Models and Simulator are mapped 1-to-1 in `python/v1-basic/api_gateway_simulator.py`. Standard library `unittest` is used in `tests/test_api_gateway_simulator.py`.
