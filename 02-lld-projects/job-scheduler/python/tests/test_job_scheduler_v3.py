import unittest
import threading
import time
from typing import List
import sys
import os
import importlib.util

try:
    from v3_optimized.job_scheduler import JobScheduler, TaskState, DAGTask, ScheduledThreadPoolExecutor, DAGScheduler
except ImportError:
    def load_module_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized', 'job_scheduler.py')
    job_scheduler = load_module_from_path('job_scheduler', file_path)
    
    JobScheduler = job_scheduler.JobScheduler
    TaskState = job_scheduler.TaskState
    DAGTask = job_scheduler.DAGTask
    ScheduledThreadPoolExecutor = job_scheduler.ScheduledThreadPoolExecutor
    DAGScheduler = job_scheduler.DAGScheduler

class TestV3(unittest.TestCase):
    def test_v3_sanity(self) -> None:
        scheduler = JobScheduler()
        self.assertIsNotNone(scheduler.describe())
        scheduler.executor.stop()

    def test_concurrent_dag_execution(self) -> None:
        executor = ScheduledThreadPoolExecutor(max_workers=8)
        executor.start()
        
        dag_scheduler = DAGScheduler(executor)
        
        completed_tasks = []
        lock = threading.Lock()
        
        def make_action(name: str, delay: float = 0.01):
            def action():
                time.sleep(delay)
                with lock:
                    completed_tasks.append(name)
                return name
            return action

        # Create a DAG:
        # A -> B -> D
        #   -> C -> D
        # A -> E
        
        taskA = DAGTask("A", make_action("A"), dependencies=[])
        taskB = DAGTask("B", make_action("B"), dependencies=["A"])
        taskC = DAGTask("C", make_action("C"), dependencies=["A"])
        taskD = DAGTask("D", make_action("D"), dependencies=["B", "C"])
        taskE = DAGTask("E", make_action("E"), dependencies=["A"])
        
        for t in [taskA, taskB, taskC, taskD, taskE]:
            dag_scheduler.add_task(t)
            
        dag_scheduler.submit_dag()
        
        # Wait for all tasks to complete or timeout
        for t in [taskA, taskB, taskC, taskD, taskE]:
            t.wait_for_completion(timeout=2.0)
            
        # Send a poison pill / explicitly stop workers and drain queue to prevent flaky test failures due to race conditions
        executor.stop()
        
        # Verify states
        for t in [taskA, taskB, taskC, taskD, taskE]:
            self.assertEqual(t.state, TaskState.COMPLETED)
            
        # Verify topological order
        a_index = completed_tasks.index("A")
        b_index = completed_tasks.index("B")
        c_index = completed_tasks.index("C")
        d_index = completed_tasks.index("D")
        e_index = completed_tasks.index("E")
        
        self.assertLess(a_index, b_index)
        self.assertLess(a_index, c_index)
        self.assertLess(b_index, d_index)
        self.assertLess(c_index, d_index)
        self.assertLess(a_index, e_index)
        
        self.assertEqual(len(completed_tasks), 5)

if __name__ == "__main__":
    unittest.main()
