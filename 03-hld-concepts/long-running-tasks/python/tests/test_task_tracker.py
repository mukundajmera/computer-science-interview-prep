import pytest
import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from task_tracker import TaskTracker, TaskContext, TaskInfo, TaskStatus

@pytest.fixture
def tracker():
    tracker = TaskTracker()
    yield tracker
    tracker.shutdown()

def test_successful_task_execution(tracker):
    event = threading.Event()
    callback_info = {}

    def action(context: TaskContext):
        context.set_progress(50)
        time.sleep(0.05)
        context.set_progress(100)
        return "Success Output"

    def callback(info: TaskInfo):
        callback_info['info'] = info
        event.set()

    task_id = tracker.submit_task(action, callback)

    # Task should be queued or running
    info = tracker.get_task_info(task_id)
    assert info is not None
    assert info.status in (TaskStatus.QUEUED, TaskStatus.RUNNING)

    event.wait(timeout=2.0)

    assert event.is_set()
    final_info = tracker.get_task_info(task_id)
    assert final_info.status == TaskStatus.COMPLETED
    assert final_info.progress == 100
    assert final_info.result == "Success Output"
    assert final_info.error is None

    assert callback_info['info'].status == TaskStatus.COMPLETED
    assert callback_info['info'].result == "Success Output"

def test_task_failure(tracker):
    event = threading.Event()

    def action(context: TaskContext):
        raise ValueError("Simulated Error")

    def callback(info: TaskInfo):
        event.set()

    task_id = tracker.submit_task(action, callback)
    event.wait(timeout=2.0)

    final_info = tracker.get_task_info(task_id)
    assert final_info.status == TaskStatus.FAILED
    assert final_info.error == "Simulated Error"
    assert final_info.result is None

def test_task_cancellation(tracker):
    started_event = threading.Event()
    finished_event = threading.Event()

    def action(context: TaskContext):
        started_event.set()
        while not context.is_cancelled():
            time.sleep(0.01)
        return "Should not return this"

    def callback(info: TaskInfo):
        finished_event.set()

    task_id = tracker.submit_task(action, callback)

    started_event.wait(timeout=2.0)
    info = tracker.get_task_info(task_id)
    assert info.status == TaskStatus.RUNNING

    cancelled = tracker.cancel_task(task_id)
    assert cancelled is True

    finished_event.wait(timeout=2.0)

    final_info = tracker.get_task_info(task_id)
    assert final_info.status == TaskStatus.CANCELLED

def test_cancel_non_existent_task(tracker):
    assert tracker.cancel_task("invalid-id") is False