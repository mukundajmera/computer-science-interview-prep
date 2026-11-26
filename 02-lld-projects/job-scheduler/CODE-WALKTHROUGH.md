# Code Walkthrough: Job Scheduler v1 (Basic)

This walkthrough traces the execution path of the **Job Scheduler (v1-basic)** to demonstrate how jobs are defined, scheduled, validated, and executed in an in-memory queue. It covers job lifecycle and progression with bounded concurrency and DAG dependencies.

## 1. Job Definition and State Lifecycle
The `Job` class models a unit of execution. It holds metadata, the `action` logic, a `RetryPolicy`, an optional `cronExpression`, and `dependencies` (for DAGs). The `JobStatus` enum transitions through states: `CREATED -> SCHEDULED -> RUNNING -> SUCCEEDED | FAILED | RETRYING`. It also supports `CANCELLED`.

A `Job` is instantiated like this:
```java
Job job = new Job("my_job_id", () -> {
    // Execution logic
}, null, new RetryPolicy(2, 1000, 2.0), Arrays.asList("dep_job_id"));
```

When submitted to `JobScheduler`, it performs dependency and cycle resolution.

## 2. Scheduling and Validation (DAGs)
When `scheduleJob(Job)` is called on the `JobScheduler`, it evaluates the job's constraints:
1. **Dependency Verification:** It ensures all `dependencies` are known to the `JobStore`.
2. **Cycle Detection:** It performs a Depth First Search (DFS) on the dependency graph to guarantee no cycles exist (preventing deadlocks).
3. **Execution Delay:** It computes `nextExecutionTime` based on the system `Clock` (or `cronExpression`).
4. **Queue Admission:** If dependencies are fully resolved (i.e. all dependencies have `SUCCEEDED`), it changes the state to `SCHEDULED` and submits it to the `JobExecutor`. Otherwise, it remains `CREATED` and waits.

## 3. Job Executor and Bounded Priority Queue
The `JobExecutor` consumes jobs from a bounded concurrent priority queue (`PriorityBlockingQueue` in Java, `heapq` with locks in Python). The queue is ordered by `nextExecutionTime`. It prevents queue saturation by rejecting new jobs if the capacity is exceeded.

Worker threads perform the following logic:
```java
private void workerLoop() {
    while (running) {
        // Poll and peek for jobs
        // Sleep if the head of the queue is due in the future
        // Pop and execute when a job is ready
    }
}
```
The execution runs the job's `action`. If it succeeds, dependents are notified to trigger subsequent jobs in the DAG. If it fails, a retry delay is computed based on `RetryPolicy`, and the job re-enters the queue with state `RETRYING`.

## 4. Deterministic Testing
A significant feature of `v1-basic` is its testability. Both Python and Java expose an injectable `Clock` interface (`TestClock`). By manipulating the clock directly, tests can instantly verify backoff delays, cron calculation, deterministic due-time ordering, and timeouts without sleeping the actual thread. 

## Summary
The combination of `JobScheduler` for DAG state machines and `JobExecutor` for bounded, time-aware execution threads forms the baseline contract for the subsequent variants (`v2-extended` and `v3-optimized`).

## 5. Contracts and Guarantees

To ensure robust workflow execution, the implementation adheres strictly to these explicit domain contracts:

### Exactly-Once Execution Transitions
When multiple worker threads poll the priority queue concurrently, strict lock synchronization ensures a scheduled job is safely transitioned to `RUNNING` precisely once, preventing overlapping executions.

**Java:**
```java
synchronized (lock) {
    if (!running) break;
    // ...
    QueueItem item = queue.poll();
    if (item != null) {
        Job job = item.getJob();
        // Prevent concurrent execution of the same job if already executing
        if (job.getStatus() != JobStatus.SCHEDULED && job.getStatus() != JobStatus.RETRYING) {
            continue; 
        }
        
        job.setStatus(JobStatus.RUNNING);
        jobStore.saveJob(job);
        jobToExecute = job;
    }
}
```

**Python:**
```python
with self._condition:
    if not self._running:
        break
    # ...
    heapq.heappop(self._queue)
    job = next_item.job

    # Prevent concurrent execution of the same job
    if job.status not in (JobStatus.SCHEDULED, JobStatus.RETRYING):
        continue
    
    job.status = JobStatus.RUNNING
    self.job_store.save_job(job)
```

### DAG Failure Isolation
The scheduler respects strict DAG dependency semantics. If a parent job fails permanently, its dependent nodes will never be released, preserving safety by avoiding execution with missing inputs. Dependents are only released when the parent successfully completes and reaches `SUCCEEDED` status.

**Java:**
```java
private void onJobCompleted(Job completedJob) {
    if (completedJob.getStatus() == JobStatus.SUCCEEDED) {
        synchronized (lock) {
            List<String> dependents = dependentJobs.getOrDefault(completedJob.getId(), Collections.emptyList());
            for (String childId : dependents) {
                Job childJob = jobStore.getJob(childId);
                // Only release child if ALL dependencies are met
                if (childJob != null && childJob.getStatus() == JobStatus.CREATED) {
                    if (areDependenciesMet(childJob)) {
                        childJob.setStatus(JobStatus.SCHEDULED);
                        jobStore.saveJob(childJob);
                        executor.submit(childJob);
                    }
                }
            }
        }
    }
}
```

**Python:**
```python
def _on_job_completed(self, completed_job: Job) -> None:
    if completed_job.status == JobStatus.SUCCEEDED:
        with self._lock:
            dependents = self._dependent_jobs.get(completed_job.id, [])
            for child_id in dependents:
                child_job = self.job_store.get_job(child_id)
                # Only release child if ALL dependencies are met
                if child_job and child_job.status == JobStatus.CREATED:
                    if self._are_dependencies_met(child_job):
                        child_job.status = JobStatus.SCHEDULED
                        self.job_store.save_job(child_job)
                        self.executor.submit(child_job)
```

### Deterministic Edge-Case Coverage
Through the injection of an abstract test clock (`TestClock`), bounded structures (`executor_capacity`), and explicit state mechanisms, tests deterministically validate cycles (via DFS during `schedule_job`), missing dependencies, exact cancellations, saturated queues throwing exceptions, and reliable time-based ordering without flaky non-deterministic sleep calls.


## 6. Version Deltas

The codebase iteratively builds complexity across three distinct packages. While `v1-basic` forms the core, `v2-extended` and `v3-optimized` introduce additional structures to address extensibility and concurrency optimization. Tests are explicitly targeted at their respective versions to ensure feature deltas are validated in isolation.

### v2-extended: Extensibility and Observability
In `v2-extended`, the scheduler loop is generalized. Pluggable triggers and policies are introduced:
- `ExponentialBackoffPolicy`: Encapsulates retry math.
- `Trigger`: Abstractions like `OneTimeTrigger` and `FixedIntervalTrigger` separate chronological rules from job payloads.
- `SchedulerMetrics`: Counters for observability (queued, running, failed).

### v3-optimized: Bounded Boundedness and Distributed Simulation
The `v3-optimized` namespace demonstrates mechanisms necessary for concurrency bounds and distributed scaling simulations within an in-memory test harness:
- `BoundedTaskQueue`: Implements strict saturation rejection, preventing `OutOfMemoryError` during massive DAG fan-outs.
- `DAGTask` and `DAGScheduler`: Employs robust synchronization constructs (`ReentrantLock`, `Condition` in Java; `threading.Lock`, `threading.Condition` in Python) to safely manage parent-child signal propagation.
- Distributed Dummy Placeholders: Contains placeholder interfaces for `IdempotencyStore`, `LeaseManager`, `RecoveryManager`, and `ShardManager` to illustrate the architectural slots required for distributed storage and execution consistency.
