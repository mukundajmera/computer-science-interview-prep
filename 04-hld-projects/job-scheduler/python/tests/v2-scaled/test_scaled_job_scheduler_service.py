import time
import pytest
import threading
import sys
import os

# Ensure the module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

from scaled_job_scheduler_service import ScaledJobSchedulerService, JobStatus

def test_job_dependencies():
    scheduler = ScaledJobSchedulerService()
    results = []

    def task1():
        results.append("task1")

    def task2():
        results.append("task2")

    job1_id = scheduler.submit_one_off_job(task1, 100, 0, 100)
    job2_id = scheduler.submit_one_off_job(task2, 0, 0, 100, dependencies=[job1_id])

    time.sleep(0.3)
    assert results == ["task1", "task2"]
    assert scheduler.get_job_status(job1_id) == JobStatus.SUCCEEDED
    assert scheduler.get_job_status(job2_id) == JobStatus.SUCCEEDED
    scheduler.shutdown()

def test_dead_letter_queue():
    scheduler = ScaledJobSchedulerService()

    def failing_task():
        raise Exception("Failed task")

    job_id = scheduler.submit_one_off_job(failing_task, 0, 2, 50) # 3 attempts
    time.sleep(0.5)

    assert scheduler.get_job_status(job_id) == JobStatus.DEAD_LETTER
    dlq = scheduler.get_dead_letter_queue()
    assert len(dlq) == 1
    assert dlq[0][0] == job_id
    scheduler.shutdown()

def test_pause_resume():
    scheduler = ScaledJobSchedulerService()
    results = []

    def task():
        results.append("task")

    job_id = scheduler.submit_one_off_job(task, 100, 0, 100)
    assert scheduler.pause_job(job_id) == True
    assert scheduler.get_job_status(job_id) == JobStatus.PAUSED

    time.sleep(0.2)
    assert len(results) == 0 # Should not have run

    assert scheduler.resume_job(job_id) == True
    time.sleep(0.2)
    assert len(results) == 1
    scheduler.shutdown()

def test_worker_eviction_and_lease_reassignment():
    scheduler = ScaledJobSchedulerService(lease_duration_ms=200)
    scheduler.register_worker("worker1")

    class BlockingTask:
        def __init__(self):
            self.started = False
            self.finish = False
            self.lock = threading.Condition()
            self.runs = 0

        def __call__(self):
            with self.lock:
                self.runs += 1
                self.started = True
                self.lock.notify_all()
            while not self.finish:
                time.sleep(0.1)

    task = BlockingTask()
    job_id = scheduler.submit_one_off_job(task, 0, 1, 10)

    # Wait for task to start
    with task.lock:
        if not task.started:
            task.lock.wait(1.0)

    assert task.started
    assert scheduler.get_job_status(job_id) == JobStatus.RUNNING

    # Wait for lease to expire
    time.sleep(0.5)

    # The coordinator should detect lease expiry and reassign/retry
    # Wait for it to restart
    time.sleep(0.3)

    with task.lock:
        assert task.runs > 1 # It should have run a second time due to lease expiry

    task.finish = True
    scheduler.shutdown()
