import time
import uuid
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from schema_validator import SchemaValidator
from rate_limited_executor import RateLimitedExecutor, RateLimitExceeded

class ToolCallV2:
    def __init__(self, tool_name: str, arguments: Dict[str, Any] = None, dependencies: List[str] = None, call_id: str = None):
        self.tool_name = tool_name
        self.arguments = arguments or {}
        self.dependencies = dependencies or []
        self.call_id = call_id or str(uuid.uuid4())

class ToolResultV2:
    def __init__(self, call_id: str, tool_name: str, success: bool, result: Any = None, error: str = None, duration_ms: float = 0.0):
        self.call_id = call_id
        self.tool_name = tool_name
        self.success = success
        self.result = result
        self.error = error
        self.duration_ms = duration_ms

class ParallelRouter:
    """Parallel tool router with DAG dependency resolution."""

    def __init__(self, registry: Any, max_workers: int = 4, rate_limiter: Optional[RateLimitedExecutor] = None):
        self._registry = registry
        self.max_workers = max_workers
        self.rate_limiter = rate_limiter

    def route_parallel(self, calls: List[ToolCallV2]) -> List[ToolResultV2]:
        """Routes multiple calls concurrently, respecting dependencies."""

        # Build DAG
        dependencies: Dict[str, set] = {call.call_id: set(call.dependencies) for call in calls}
        call_map: Dict[str, ToolCallV2] = {call.call_id: call for call in calls}

        results: Dict[str, ToolResultV2] = {}
        completed: set = set()

        # We need a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map future to call_id
            future_to_call_id = {}

            while len(completed) < len(calls):
                # Find calls with all dependencies met that haven't been scheduled
                ready_calls = []
                for call_id, deps in dependencies.items():
                    if call_id not in completed and call_id not in future_to_call_id.values():
                        # Check if all dependencies are in completed
                        # and that all dependent tools were successful
                        can_run = True
                        for dep in deps:
                            if dep not in completed:
                                can_run = False
                                break
                            if dep in results and not results[dep].success:
                                can_run = False
                                break

                        if can_run:
                            ready_calls.append(call_id)

                # If there are ready calls, submit them
                if ready_calls:
                    for call_id in ready_calls:
                        call = call_map[call_id]
                        # Create future
                        future = executor.submit(self._execute_single_call, call)
                        future_to_call_id[future] = call_id

                # If no calls are ready and no futures are running, we have a cycle or unresolvable dependencies
                if not ready_calls and not future_to_call_id:
                    # Mark remaining as failed
                    for call_id in call_map:
                        if call_id not in completed:
                            results[call_id] = ToolResultV2(
                                call_id=call_id,
                                tool_name=call_map[call_id].tool_name,
                                success=False,
                                error="Dependency resolution failed or cyclic dependency"
                            )
                            completed.add(call_id)
                    break

                # Wait for at least one future to complete
                # as_completed returns an iterator, we use it just to wait for the next completion
                if future_to_call_id:
                    # We can't easily wait for "any" using as_completed in a non-blocking way
                    # without popping the first one. We use concurrent.futures.wait with FIRST_COMPLETED
                    import concurrent.futures
                    done, _ = concurrent.futures.wait(future_to_call_id.keys(), return_when=concurrent.futures.FIRST_COMPLETED)

                    for future in done:
                        call_id = future_to_call_id.pop(future)
                        try:
                            result = future.result()
                            results[call_id] = result
                        except Exception as e:
                            # Catch unexpected exceptions in executor
                            call = call_map[call_id]
                            results[call_id] = ToolResultV2(
                                call_id=call_id,
                                tool_name=call.tool_name,
                                success=False,
                                error=f"Unexpected error: {e}"
                            )
                        completed.add(call_id)

                        # If a tool failed, we might want to mark its dependents as failed too,
                        # but our loop condition handles it by simply never scheduling them.
                        # Wait, we need to handle them so they get marked as failed and completed.
                        if not results[call_id].success:
                            self._fail_dependents(call_id, dependencies, call_map, results, completed)

        # Return results in the order of original calls
        return [results[call.call_id] for call in calls]

    def _fail_dependents(self, failed_call_id: str, dependencies: Dict[str, set], call_map: Dict[str, ToolCallV2], results: Dict[str, ToolResultV2], completed: set):
        """Recursively fails all dependent calls."""
        for call_id, deps in dependencies.items():
            if call_id not in completed and failed_call_id in deps:
                results[call_id] = ToolResultV2(
                    call_id=call_id,
                    tool_name=call_map[call_id].tool_name,
                    success=False,
                    error=f"Dependency failed: {failed_call_id}"
                )
                completed.add(call_id)
                self._fail_dependents(call_id, dependencies, call_map, results, completed)

    def _execute_single_call(self, call: ToolCallV2) -> ToolResultV2:
        start = time.time()

        tool_def = self._registry.get(call.tool_name)
        if not tool_def:
            return ToolResultV2(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Unknown tool: {call.tool_name}",
                duration_ms=self._elapsed_ms(start)
            )

        # Validate with repair logic using SchemaValidator
        validator = SchemaValidator(tool_def.parameter_schema.parameters if hasattr(tool_def.parameter_schema, 'parameters') else getattr(tool_def.parameter_schema, '_parameters', {}))
        success, repaired_args, errors = validator.validate_and_repair(call.arguments)

        if not success:
            return ToolResultV2(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error="Validation failed: " + "; ".join(errors),
                duration_ms=self._elapsed_ms(start)
            )

        try:
            if self.rate_limiter:
                # Assuming cost is 1 per call for simplicity
                result_val = self.rate_limiter.execute(call.tool_name, tool_def.handler, repaired_args)
            else:
                result_val = tool_def.handler(repaired_args)

            return ToolResultV2(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=True,
                result=result_val,
                duration_ms=self._elapsed_ms(start)
            )
        except RateLimitExceeded as rle:
            return ToolResultV2(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Rate limit error: {rle}",
                duration_ms=self._elapsed_ms(start)
            )
        except Exception as e:
            return ToolResultV2(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Handler error: {e}",
                duration_ms=self._elapsed_ms(start)
            )

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        return (time.time() - start) * 1000.0
