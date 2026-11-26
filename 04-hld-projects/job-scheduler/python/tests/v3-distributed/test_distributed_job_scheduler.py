import pytest
import sys
import os

# dynamic sys.path import to allow testing the hyphenated directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_job_scheduler import DistributedJobScheduler, Datastore, JobState

def create_mock_handler(executed_jobs):
    def handler(job_id: str, token: str) -> bool:
        executed_jobs.add(job_id)
        return True
    return handler

def create_fail_handler():
    def handler(job_id: str, token: str) -> bool:
        return False
    return handler

def test_basic_scheduling_and_execution():
    datastore = Datastore()
    executed = set()
    node1 = DistributedJobScheduler("node-1", datastore, create_mock_handler(executed))

    datastore.submit_job("job-1", 1000)

    node1.tick(500)
    assert node1.is_leader
    assert datastore.get_job("job-1").state == JobState.SCHEDULED

    node1.tick(1000)
    assert datastore.get_job("job-1").state == JobState.COMPLETED
    assert "job-1" in executed
    assert datastore.get_job("job-1").attempt == 1

def test_consistent_hashing_assignment():
    datastore = Datastore()
    executed1 = set()
    executed2 = set()
    node1 = DistributedJobScheduler("node-1", datastore, create_mock_handler(executed1))
    node2 = DistributedJobScheduler("node-2", datastore, create_mock_handler(executed2))

    datastore.submit_job("job-1", 1000)
    datastore.submit_job("job-2", 1000)
    datastore.submit_job("job-3", 1000)
    datastore.submit_job("job-4", 1000)

    node1.tick(500)
    node2.tick(500)

    node1.tick(1000)
    node2.tick(1000)

    assert node1.is_leader or node2.is_leader

    assert datastore.get_job("job-1").state == JobState.COMPLETED
    assert datastore.get_job("job-2").state == JobState.COMPLETED
    assert datastore.get_job("job-3").state == JobState.COMPLETED
    assert datastore.get_job("job-4").state == JobState.COMPLETED

    assert len(executed1) + len(executed2) == 4

def test_worker_failover():
    datastore = Datastore()
    executed2 = set()
    node1 = DistributedJobScheduler("node-1", datastore, create_fail_handler())
    node2 = DistributedJobScheduler("node-2", datastore, create_mock_handler(executed2))

    datastore.submit_job("job-1", 1000)

    node1.tick(1000)
    assert datastore.get_job("job-1").state == JobState.FAILED

    # we need node2 to become the leader in order to reassign the job.
    # node1 stops heartbeating.
    # let node2 tick enough to claim leadership and notice node1 is gone or just wait.
    node2.tick(1500)
    node2.tick(6500) # Now node2 is definitely leader and reassigns

    assert datastore.get_job("job-1").state == JobState.COMPLETED

def test_idempotency_token():
    datastore = Datastore()
    execution_count = [0]

    def idempotent_handler(job_id: str, token: str) -> bool:
        execution_count[0] += 1
        return True

    node1 = DistributedJobScheduler("node-1", datastore, idempotent_handler)

    datastore.submit_job("job-1", 1000)

    node1.tick(1000)
    assert datastore.get_job("job-1").state == JobState.COMPLETED
    assert execution_count[0] == 1

    datastore.get_job("job-1").state = JobState.RUNNING
    datastore.get_job("job-1").lease_until = 3000

    node1.tick(2000)

    assert datastore.get_job("job-1").state == JobState.COMPLETED
    assert execution_count[0] == 1

def test_leader_election():
    datastore = Datastore()
    node1 = DistributedJobScheduler("node-1", datastore, create_mock_handler(set()))
    node2 = DistributedJobScheduler("node-2", datastore, create_mock_handler(set()))

    node1.tick(100)
    assert node1.is_leader

    node2.tick(200)
    assert not node2.is_leader

    node2.tick(5500)
    assert node2.is_leader

    node1.tick(5600)
    assert not node1.is_leader

def test_dead_letter():
    datastore = Datastore()
    node1 = DistributedJobScheduler("node-1", datastore, create_fail_handler())

    datastore.submit_job("job-1", 1000)

    node1.tick(1000)
    node1.tick(2000)
    node1.tick(3000)
    node1.tick(4000)

    assert datastore.get_job("job-1").state == JobState.DEAD_LETTER
    assert datastore.get_job("job-1").attempt == 4
