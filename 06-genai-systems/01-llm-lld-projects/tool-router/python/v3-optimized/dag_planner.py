import re
from typing import Any, Dict, List, Set, Tuple

class DAGPlannerError(Exception):
    pass

class CyclicDependencyError(DAGPlannerError):
    pass

class ToolCallV3:
    def __init__(self, tool_name: str, arguments: Dict[str, Any] = None, dependencies: List[str] = None, call_id: str = None):
        import uuid
        self.tool_name = tool_name
        self.arguments = arguments or {}
        self.dependencies = dependencies or []
        self.call_id = call_id or str(uuid.uuid4())

class DAGPlanner:
    """
    DAG tool execution planner that resolves interdependent tool arguments,
    detects dependency cycles, and plans execution into concurrent stages.
    """

    def __init__(self):
        # Matches $call_id or $call_id.field
        self._ref_pattern = re.compile(r'^\$([^.]+)(?:\.(.+))?$')

    def plan_stages(self, calls: List[ToolCallV3]) -> List[List[ToolCallV3]]:
        """
        Groups tool calls into stages that can be executed concurrently.
        Detects cyclic dependencies.
        """
        call_map = {call.call_id: call for call in calls}
        dependencies: Dict[str, Set[str]] = {
            call.call_id: set(call.dependencies) for call in calls
        }

        for call_id, deps in dependencies.items():
            for dep in deps:
                if dep not in call_map:
                    raise DAGPlannerError(f"Dependency {dep} for call {call_id} not found in provided calls.")

        stages: List[List[ToolCallV3]] = []
        resolved: Set[str] = set()

        while len(resolved) < len(calls):
            current_stage_ids = [
                call_id for call_id, deps in dependencies.items()
                if call_id not in resolved and deps.issubset(resolved)
            ]

            if not current_stage_ids:
                unresolved = set(call_map.keys()) - resolved
                raise CyclicDependencyError(f"Dependency cycle detected among calls: {unresolved}")

            stages.append([call_map[cid] for cid in current_stage_ids])
            resolved.update(current_stage_ids)

        return stages

    def resolve_arguments(self, call: ToolCallV3, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves dynamic arguments in a tool call based on results from previous calls.
        For example, if an argument is "$call_1", it will be replaced by previous_results['call_1'].
        If it is "$call_1.field", it will be replaced by previous_results['call_1']['field'].
        """
        resolved_args = {}
        for key, value in call.arguments.items():
            if isinstance(value, str):
                match = self._ref_pattern.match(value)
                if match:
                    ref_call_id, ref_field = match.groups()
                    if ref_call_id not in previous_results:
                        raise DAGPlannerError(f"Result for referenced call {ref_call_id} not found.")

                    result_data = previous_results[ref_call_id]
                    if ref_field:
                        if isinstance(result_data, dict) and ref_field in result_data:
                            resolved_args[key] = result_data[ref_field]
                        elif hasattr(result_data, ref_field):
                            resolved_args[key] = getattr(result_data, ref_field)
                        else:
                            raise DAGPlannerError(f"Field {ref_field} not found in result of call {ref_call_id}.")
                    else:
                        # Just $call_id
                        resolved_args[key] = result_data
                    continue

            resolved_args[key] = value

        return resolved_args
