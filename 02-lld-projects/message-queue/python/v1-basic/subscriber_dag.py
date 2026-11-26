from typing import Dict, List, Callable

class SubscriberDAG:
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        self.tasks: Dict[str, Callable] = {}

    def add_subscriber(self, subscriber_id: str, task: Callable):
        self.tasks[subscriber_id] = task
        if subscriber_id not in self.dependencies:
            self.dependencies[subscriber_id] = []

    def add_dependency(self, from_node: str, to_node: str):
        if from_node not in self.dependencies:
            self.dependencies[from_node] = []
        self.dependencies[from_node].append(to_node)

    def execute(self):
        in_degree = {node: 0 for node in self.tasks}
        
        for deps in self.dependencies.values():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1
                
        queue = [node for node, deg in in_degree.items() if deg == 0]
        order = []
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            for neighbor in self.dependencies.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(order) != len(self.tasks):
            raise ValueError("Cycle detected in subscriber DAG")
            
        for sub in order:
            self.tasks[sub]()
