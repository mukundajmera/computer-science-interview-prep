import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from tool import ToolDefinition
from schema import ParameterSchema
from router import ToolRegistry

from parallel_router import ParallelRouter, ToolCallV2
from rate_limited_executor import RateLimitedExecutor

def demo_v2():
    print("=== Tool Router v2 Extended Demo ===\n")

    # 1. Setup tools
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="fetch_user",
        description="Fetches user data",
        parameter_schema=ParameterSchema({"user_id": {"type": "integer", "required": True}}),
        handler=lambda args: {"id": args["user_id"], "name": f"User {args['user_id']}"}
    ))
    registry.register(ToolDefinition(
        name="fetch_orders",
        description="Fetches user orders",
        parameter_schema=ParameterSchema({"user_id": {"type": "integer", "required": True}}),
        handler=lambda args: ["Order 1", "Order 2"]
    ))

    # 2. Setup Router with Rate Limiting
    rate_limiter = RateLimitedExecutor(capacity=5, fill_rate=1.0)
    router = ParallelRouter(registry=registry, max_workers=2, rate_limiter=rate_limiter)

    # 3. Create Parallel Calls with Dependencies
    call1 = ToolCallV2(tool_name="fetch_user", arguments={"user_id": "123"}, call_id="c1") # Type coercion will fix '123' -> 123
    call2 = ToolCallV2(tool_name="fetch_orders", arguments={"user_id": 123}, dependencies=["c1"], call_id="c2")

    print(f"Executing parallel calls...")
    start = time.time()
    results = router.route_parallel([call1, call2])
    print(f"Completed in {time.time() - start:.2f}s")

    for r in results:
        print(f"[{r.call_id}] {r.tool_name} success={r.success} result={r.result} error={r.error}")

if __name__ == "__main__":
    demo_v2()
