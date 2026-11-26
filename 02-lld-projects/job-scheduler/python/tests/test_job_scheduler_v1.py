import unittest
import threading
import time
import importlib.util
import os
import sys

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
job_status_mod = load_module('job_status', os.path.join(base_dir, 'job_status.py'))
job_mod = load_module('job', os.path.join(base_dir, 'job.py'))
cron_parser_mod = load_module('cron_parser', os.path.join(base_dir, 'cron_parser.py'))
job_store_mod = load_module('job_store', os.path.join(base_dir, 'job_store.py'))
in_memory_job_store_mod = load_module('in_memory_job_store', os.path.join(base_dir, 'in_memory_job_store.py'))
clock_mod = load_module('clock', os.path.join(base_dir, 'clock.py'))
job_executor_mod = load_module('job_executor', os.path.join(base_dir, 'job_executor.py'))
job_scheduler_mod = load_module('job_scheduler', os.path.join(base_dir, 'job_scheduler.py'))

JobStatus = job_status_mod.JobStatus
Job = job_mod.Job
RetryPolicy = job_mod.RetryPolicy
CronParser = cron_parser_mod.CronParser
TestClock = clock_mod.TestClock
JobScheduler = job_scheduler_mod.JobScheduler
JobExecutor = job_executor_mod.JobExecutor
InMemoryJobStore = in_memory_job_store_mod.InMemoryJobStore

class TestV1(unittest.TestCase):
    def test_v1_sanity(self) -> None:
        scheduler = JobScheduler()
        self.assertIsNotNone(scheduler)

    def test_immediate_execution(self) -> None:
        clock = TestClock()
        scheduler = JobScheduler(clock=clock)
        scheduler.start()
        
        results = []
        event = threading.Event()
        def action():
            results.append("done")
            event.set()
            
        job = Job("job1", action)
        scheduler.schedule_job(job)
        
        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(scheduler.get_job("job1").status, JobStatus.SUCCEEDED)
        
    def test_retry_policy(self) -> None:
        clock = TestClock()
        store = InMemoryJobStore()
        
        original_save = store.save_job
        def custom_save(job):
            original_save(job)
            if job.status == JobStatus.RETRYING:
                clock.advance(50)
                
        store.save_job = custom_save
        
        executor = JobExecutor(store, clock, 100, 1)
        scheduler = JobScheduler(job_store=store, clock=clock, executor=executor)
        
        attempts = []
        event = threading.Event()
        
        def action():
            attempts.append("fail")
            if len(attempts) == 3:
                event.set()
            raise Exception("Fail")
            
        policy = RetryPolicy(max_retries=2, initial_backoff_ms=50, multiplier=1.0)
        job = Job("job2", action, retry_policy=policy)
        scheduler.schedule_job(job)
        
        scheduler.start()
        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()
        
        self.assertEqual(len(attempts), 3)
        self.assertEqual(scheduler.get_job("job2").status, JobStatus.FAILED)

    def test_dag_dependencies_and_cycles(self):
        clock = TestClock()
        scheduler = JobScheduler(clock=clock)
        scheduler.start()
        
        results = []
        event = threading.Event()
        def action(name):
            results.append(name)
            if len(results) == 3:
                event.set()

        job1 = Job("job1", lambda: action("job1"))
        job2 = Job("job2", lambda: action("job2"), dependencies=["job1"])
        job3 = Job("job3", lambda: action("job3"), dependencies=["job1", "job2"])

        job4 = Job("job4", lambda: None)
        job4.dependencies = ["job5"]
        job5 = Job("job5", lambda: None)
        job5.dependencies = ["job4"]
        
        scheduler.job_store.save_job(job5)
        
        with self.assertRaises(ValueError):
            scheduler.schedule_job(job4)

        scheduler.schedule_job(job1)
        scheduler.schedule_job(job2)
        scheduler.schedule_job(job3)

        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()

        self.assertEqual(results, ["job1", "job2", "job3"])
        self.assertEqual(scheduler.get_job("job3").status, JobStatus.SUCCEEDED)

    def test_cancellation(self):
        clock = TestClock()
        scheduler = JobScheduler(clock=clock)
        
        job = Job("job1", lambda: None)
        job.next_execution_time = clock.now() + 1000
        scheduler.schedule_job(job)
        
        self.assertTrue(scheduler.cancel_job("job1"))
        self.assertEqual(scheduler.get_job("job1").status, JobStatus.CANCELLED)

        event = threading.Event()
        job2 = Job("job2", lambda: event.set())
        job2.next_execution_time = clock.now() + 1000
        scheduler.schedule_job(job2)
        
        scheduler.start()
        clock.advance(1000)
        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()
        self.assertEqual(scheduler.get_job("job1").status, JobStatus.CANCELLED)

    def test_bounded_queue(self):
        clock = TestClock()
        scheduler = JobScheduler(clock=clock, executor_capacity=1)
        
        job1 = Job("job1", lambda: None)
        job1.next_execution_time = clock.now() + 1000
        scheduler.schedule_job(job1)

        job2 = Job("job2", lambda: None)
        with self.assertRaises(RuntimeError):
            scheduler.schedule_job(job2)

    def test_concurrent_pollers(self):
        clock = TestClock()
        scheduler = JobScheduler(clock=clock, executor_workers=3)
        scheduler.start()

        lock = threading.Lock()
        counter = 0
        event = threading.Event()

        def action():
            nonlocal counter
            with lock:
                counter += 1
                if counter == 10:
                    event.set()

        for i in range(10):
            scheduler.schedule_job(Job(f"job{i}", action))

        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()
        self.assertEqual(counter, 10)

    def test_missing_dependency(self):
        scheduler = JobScheduler()
        job1 = Job("job1", lambda: None, dependencies=["missing"])
        with self.assertRaises(ValueError):
            scheduler.schedule_job(job1)

    def test_deterministic_due_time_ordering(self):
        clock = TestClock()
        store = InMemoryJobStore()
        executor = JobExecutor(store, clock, 100, 1)
        scheduler = JobScheduler(job_store=store, clock=clock, executor=executor)
        
        event = threading.Event()
        results = []
        def action(name):
            results.append(name)
            if len(results) == 2:
                event.set()

        job2 = Job("B", lambda: action("B"))
        job2.next_execution_time = 1000
        job1 = Job("A", lambda: action("A"))
        job1.next_execution_time = 1000

        scheduler.schedule_job(job2)
        scheduler.schedule_job(job1)
        
        clock.advance(1000)
        scheduler.start()
        self.assertTrue(event.wait(timeout=2.0))
        scheduler.stop()
        
        self.assertEqual(results, ["A", "B"])

    def test_failure_does_not_release_dependents(self):
        clock = TestClock()
        store = InMemoryJobStore()
        executor = JobExecutor(store, clock, 100, 1)
        scheduler = JobScheduler(job_store=store, clock=clock, executor=executor)
        
        fail_event = threading.Event()
        completion_event = threading.Event()
        
        def completion_callback(j):
            if j.id == "job1" and j.status == JobStatus.FAILED:
                completion_event.set()
                
        executor.set_job_completion_callback(completion_callback)
        
        def fail_action():
            fail_event.set()
            raise Exception("Fail")
            
        job1 = Job("job1", fail_action, retry_policy=RetryPolicy(max_retries=0))
        job2 = Job("job2", lambda: None, dependencies=["job1"])
        
        scheduler.schedule_job(job1)
        scheduler.schedule_job(job2)
        
        scheduler.start()
        self.assertTrue(fail_event.wait(timeout=2.0))
        self.assertTrue(completion_event.wait(timeout=2.0))
        scheduler.stop()
        
        self.assertEqual(scheduler.get_job("job2").status, JobStatus.CREATED)
        
    def test_shutdown(self):
        clock = TestClock()
        scheduler = JobScheduler(clock=clock)
        scheduler.start()
        
        event = threading.Event()
        job_running_event = threading.Event()
        def action():
            job_running_event.set()
            event.wait(timeout=2.0)
            
        scheduler.schedule_job(Job("job1", action))
        
        self.assertTrue(job_running_event.wait(timeout=2.0))
        scheduler.stop()
        event.set()
        
        self.assertTrue("running=False" in scheduler.describe())

if __name__ == "__main__":
    unittest.main()
