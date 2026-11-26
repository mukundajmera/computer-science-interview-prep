import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError

from dag_planner import ToolCallV3, DAGPlanner

class SpeculativeExecutionError(Exception):
    pass

class ExecutorResult:
    def __init__(self, call_id: str, tool_name: str, success: bool, result: Any = None, error: str = None, duration_ms: float = 0.0):
        self.call_id = call_id
        self.tool_name = tool_name
        self.success = success
        self.result = result
        self.error = error
        self.duration_ms = duration_ms

class SpeculativeExecutor:
    """
    Speculative executor with timeout enforcement, sandboxed execution error isolation,
    and rollback capabilities.
    """

    def __init__(self, registry: Any, max_workers: int = 4):
        self._registry = registry
        self.max_workers = max_workers
        self.planner = DAGPlanner()

    def execute_plan(self, calls: List[ToolCallV3], timeout_per_call: float = 5.0) -> List[ExecutorResult]:
        """
        Executes a plan of tool calls, returning results.
        """
        stages = self.planner.plan_stages(calls)
        results: Dict[str, ExecutorResult] = {}
        previous_results: Dict[str, Any] = {}

        # We need a rollback stack. In a real system, tools might have a rollback function registered.
        # Here we just keep track of successful calls to rollback if needed.
        successful_calls: List[ToolCallV3] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for stage_idx, stage_calls in enumerate(stages):
                futures: Dict[Future, ToolCallV3] = {}

                # Check if any dependencies from previous stages failed.
                # If a stage has failed dependencies, we shouldn't even execute it.
                # Since DAGPlanner ensures stage N only depends on stages < N,
                # we just need to check if any required dependencies for the current stage failed.
                executable_calls = []
                for call in stage_calls:
                    can_execute = True
                    for dep_id in call.dependencies:
                        if dep_id in results and not results[dep_id].success:
                            can_execute = False
                            break

                    if can_execute:
                        executable_calls.append(call)
                    else:
                        results[call.call_id] = ExecutorResult(
                            call_id=call.call_id,
                            tool_name=call.tool_name,
                            success=False,
                            error=f"Dependency failed for call {call.call_id}"
                        )

                # Submit executable calls
                for call in executable_calls:
                    # Resolve interdependent arguments
                    try:
                        resolved_args = self.planner.resolve_arguments(call, previous_results)
                    except Exception as e:
                        results[call.call_id] = ExecutorResult(
                            call_id=call.call_id,
                            tool_name=call.tool_name,
                            success=False,
                            error=f"Argument resolution failed: {e}"
                        )
                        continue

                    # Submit to thread pool
                    future = executor.submit(self._execute_single_call, call, resolved_args)
                    futures[future] = call

                # Wait for completion of this stage with timeout
                # We iterate over futures, waiting for each with the remaining timeout.
                # To enforce timeout properly per stage, we can compute the deadline.
                stage_deadline = time.time() + timeout_per_call

                for future in futures:
                    call = futures[future]
                    time_left = stage_deadline - time.time()
                    if time_left < 0:
                        time_left = 0

                    try:
                        # Wait for the future to complete
                        res = future.result(timeout=time_left)
                        results[call.call_id] = res
                        if res.success:
                            # Add to previous_results for argument resolution in next stages
                            previous_results[call.call_id] = res.result
                            successful_calls.append(call)
                        else:
                            # Error isolation: specific call failed, we isolate it by returning error result
                            # and dependent calls will fail in the next stage
                            pass
                    except TimeoutError:
                        results[call.call_id] = ExecutorResult(
                            call_id=call.call_id,
                            tool_name=call.tool_name,
                            success=False,
                            error=f"Execution timed out after {timeout_per_call} seconds."
                        )
                    except Exception as e:
                        results[call.call_id] = ExecutorResult(
                            call_id=call.call_id,
                            tool_name=call.tool_name,
                            success=False,
                            error=f"Unexpected error: {e}"
                        )

        # Rollback logic: if we want to rollback on any failure, we could do it here.
        # But usually rollback is triggered based on a policy. The prompt asks for "rollback capabilities".
        # We'll provide a rollback method.

        # Return results in the order of original calls
        return [results.get(call.call_id, ExecutorResult(call.call_id, call.tool_name, False, error="Not executed")) for call in calls]

    def _execute_single_call(self, call: ToolCallV3, resolved_args: Dict[str, Any]) -> ExecutorResult:
        start = time.time()

        # Here we should fetch tool handler from registry
        tool_def = self._registry.get(call.tool_name)
        if not tool_def:
            return ExecutorResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Unknown tool: {call.tool_name}",
                duration_ms=self._elapsed_ms(start)
            )

        # Validate arguments using the tool's schema if it exists
        # Assuming v1-basic ParameterSchema compatibility
        if hasattr(tool_def, 'parameter_schema') and tool_def.parameter_schema:
            errors = tool_def.parameter_schema.validate(resolved_args)
            if errors:
                return ExecutorResult(
                    call_id=call.call_id,
                    tool_name=call.tool_name,
                    success=False,
                    error="Validation failed: " + "; ".join(errors),
                    duration_ms=self._elapsed_ms(start)
                )

        try:
            # Execute the sandboxed handler
            result_val = tool_def.handler(resolved_args)
            return ExecutorResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=True,
                result=result_val,
                duration_ms=self._elapsed_ms(start)
            )
        except Exception as e:
            return ExecutorResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                success=False,
                error=f"Handler error: {e}",
                duration_ms=self._elapsed_ms(start)
            )

    def rollback(self, successful_calls: List[ToolCallV3], results: List[ExecutorResult]):
        """
        Rollback capability. Iterates over successful calls in reverse order
        and attempts to call a rollback handler if available in the tool registry.
        """
        for call in reversed(successful_calls):
            tool_def = self._registry.get(call.tool_name)
            # Assuming tool_def might have a rollback_handler
            if tool_def and hasattr(tool_def, 'rollback_handler') and tool_def.rollback_handler:
                try:
                    # Find the result for this call to pass to rollback
                    res = next((r for r in results if r.call_id == call.call_id), None)
                    if res and res.success:
                        tool_def.rollback_handler(call.arguments, res.result)
                except Exception as e:
                    # Best effort rollback
                    pass

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        return (time.time() - start) * 1000.0
