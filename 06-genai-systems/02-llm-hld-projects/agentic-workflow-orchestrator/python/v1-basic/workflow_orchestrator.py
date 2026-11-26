import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class WorkflowState:
    def __init__(self, initial_state: Dict[str, Any] = None):
        self.state = initial_state or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def update(self, key: str, value: Any):
        self.state[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return self.state.copy()

class StepResult:
    def __init__(self, status: str, output: Any = None, next_step: Optional[str] = None, error: Optional[Exception] = None):
        self.status = status # 'SUCCESS', 'FAIL', 'END'
        self.output = output
        self.next_step = next_step
        self.error = error

class Node:
    def __init__(self, name: str, action: Callable[[WorkflowState], StepResult], max_retries: int = 0):
        self.name = name
        self.action = action
        self.max_retries = max_retries

    def execute(self, state: WorkflowState) -> StepResult:
        retries = 0
        while retries <= self.max_retries:
            try:
                result = self.action(state)
                return result
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    return StepResult(status='FAIL', error=e)

class WorkflowOrchestrator:
    def __init__(self, max_steps: int = 50):
        self.nodes: Dict[str, Node] = {}
        self.start_node: Optional[str] = None
        self.max_steps = max_steps

    def add_node(self, node: Node, is_start: bool = False):
        self.nodes[node.name] = node
        if is_start or self.start_node is None:
            self.start_node = node.name

    def execute(self, initial_state: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        if not self.start_node:
            raise ValueError("No start node defined.")

        state = WorkflowState(initial_state)
        current_node_name = self.start_node
        step_count = 0

        while current_node_name and current_node_name != 'END':
            if step_count >= self.max_steps:
                return 'MAX_STEPS_EXCEEDED', state.to_dict()

            node = self.nodes.get(current_node_name)
            if not node:
                raise ValueError(f"Node '{current_node_name}' not found.")

            result = node.execute(state)

            if result.status == 'SUCCESS':
                current_node_name = result.next_step
            elif result.status == 'FAIL':
                # Can be a fallback node or end with failure
                if result.next_step:
                     current_node_name = result.next_step
                else:
                     return 'FAILED', state.to_dict()
            elif result.status == 'END':
                break

            step_count += 1

        return 'COMPLETED', state.to_dict()
