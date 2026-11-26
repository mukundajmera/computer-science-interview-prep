import time
import threading
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from job_scheduler_service import JobSchedulerService, JobStatus

@pytest.fixture
def scheduler():
    sched = JobSchedulerService()
    yield sched
    sched.shutdown()

def test_one_off_job_success(scheduler):
    event = threading.Event()

    def task():
        event.set()

    job_id = scheduler.submit_one_off_job(task, delay_ms=100, max_retries=3, initial_backoff_ms=100)
    assert scheduler.get_job_status(job_id) == JobStatus.SCHEDULED

    assert event.wait(timeout=2.0)

    time.sleep(0.1)  # allow state update
    assert scheduler.get_job_status(job_id) == JobStatus.SUCCEEDED

def test_periodic_job_execution(scheduler):
    events = []
    lock = threading.Lock()
    event_cond = threading.Condition(lock)

    def task():
        with event_cond:
            events.append(time.time())
            if len(events) >= 3:
                event_cond.notify()

    job_id = scheduler.submit_periodic_job(task, initial_delay_ms=50, period_ms=100, max_retries=3, initial_backoff_ms=100)

    with event_cond:
        event_cond.wait_for(lambda: len(events) >= 3, timeout=2.0)

    assert len(events) >= 3

    status = scheduler.get_job_status(job_id)
    assert status in (JobStatus.SCHEDULED, JobStatus.RUNNING)

    scheduler.cancel_job(job_id)
    assert scheduler.get_job_status(job_id) == JobStatus.CANCELLED

def test_job_failure_and_retry_with_backoff(scheduler):
    run_count = 0
    event = threading.Event()
    lock = threading.Lock()

    def task():
        nonlocal run_count
        with lock:
            run_count += 1
            current = run_count
        if current <= 2:
            raise RuntimeError("Intentional failure")
        event.set()

    job_id = scheduler.submit_one_off_job(task, delay_ms=50, max_retries=3, initial_backoff_ms=100)

    assert event.wait(timeout=3.0)

    time.sleep(0.1)
    assert scheduler.get_job_status(job_id) == JobStatus.SUCCEEDED
    assert run_count == 3

def test_job_exhausts_retries_and_fails(scheduler):
    run_count = 0
    event_cond = threading.Condition()

    def task():
        nonlocal run_count
        with event_cond:
            run_count += 1
            if run_count >= 4: # 1 initial + 3 retries
                event_cond.notify()
        raise RuntimeError("Persistent failure")

    job_id = scheduler.submit_one_off_job(task, delay_ms=50, max_retries=3, initial_backoff_ms=50)

    with event_cond:
        event_cond.wait_for(lambda: run_count >= 4, timeout=2.0)

    time.sleep(0.1)
    assert scheduler.get_job_status(job_id) == JobStatus.FAILED

def test_cancel_job(scheduler):
    def task():
        time.sleep(0.5)

    job_id = scheduler.submit_one_off_job(task, delay_ms=100, max_retries=0, initial_backoff_ms=0)

    assert scheduler.cancel_job(job_id) == True
    assert scheduler.get_job_status(job_id) == JobStatus.CANCELLED
