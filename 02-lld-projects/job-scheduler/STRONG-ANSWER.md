# Job Scheduler - Strong Interview Answer

**Time Target:** 45 minutes

## 1. Core Architecture and Determinism
**Say:** "My scheduler architecture centers around a deterministic execution loop modeled with an injected `Clock` and bounded thread pool `JobExecutor`. By controlling time and concurrency bounds explicitly, we can achieve exactly-once processing guarantees and comprehensively validate complex workflows like DAG execution, failure retries, and system shutdowns. This provides the predictability necessary for robust workflow engines."

## 2. DAG Execution & Cycle Safety
**Say:** "To handle DAG workflows, I enforce a strict state machine. Jobs initialize in the `CREATED` state. They transition to `SCHEDULED` only when all declared parent dependencies are verified as `SUCCEEDED`. If a parent job fails permanently—exhausting its `RetryPolicy`—the scheduler intentionally traps its dependents in the `CREATED` state. This prevents partial execution. To ensure topological validity, I implement a depth-first search cycle detection algorithm at submission time. A job introducing a cycle is aggressively rejected."

## 3. Concurrency Bounds & Execution Semantics
**Say:** "Concurrency is governed by a thread pool reading from a bounded priority queue. When the executor queue reaches its explicit capacity limit, the scheduler dynamically enforces backpressure by rejecting new submissions with an `IllegalStateException` or `RuntimeError`. The exactly-once transition from `SCHEDULED` to `RUNNING` under concurrent pollers is ensured by taking atomic pulls from the synchronized priority queue. A shutdown initiates a graceful interrupt, flagging pollers to stop checking the queue and exit once running tasks conclude."

## 4. Implementation Details and Full Parity Equivalent Code
**Say:** "The standard library logic is structurally identical across Java and Python. We synchronize access over the queue and mutable state maps, and ensure callback mechanics coordinate without race conditions."

### Java Implementation Snippet
```java
public class JobExecutor {
    // ...
    private final PriorityBlockingQueue<Job> queue;
    private final AtomicBoolean isRunning = new AtomicBoolean(false);

    public void start() {
        if (isRunning.compareAndSet(false, true)) {
            for (int i = 0; i < maxWorkers; i++) {
                Thread t = new Thread(this::pollLoop, "Worker-" + i);
                workers.add(t);
                t.start();
            }
        }
    }

    private void pollLoop() {
        while (isRunning.get() || !queue.isEmpty()) {
            try {
                Job job = queue.poll(100, TimeUnit.MILLISECONDS);
                if (job != null && job.getStatus() == JobStatus.SCHEDULED) {
                    job.setStatus(JobStatus.RUNNING);
                    jobStore.saveJob(job);
                    executeJob(job);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

### Python Implementation Snippet
```python
class JobExecutor:
    # ...
    def start(self):
        with self._lock:
            if not self.is_running:
                self.is_running = True
                for i in range(self.max_workers):
                    t = threading.Thread(target=self._poll_loop, name=f"Worker-{i}", daemon=True)
                    self.workers.append(t)
                    t.start()

    def _poll_loop(self):
        while self.is_running or not self.queue.empty():
            try:
                # Wait boundedly to allow shutdown checks
                item = self.queue.get(timeout=0.1)
                job = item.job
                if job.status == JobStatus.SCHEDULED:
                    job.status = JobStatus.RUNNING
                    self.job_store.save_job(job)
                    self._execute_job(job)
            except queue.Empty:
                continue
```

## 5. Version Progression
**Say:** "The architecture naturally evolves:
- `v1-basic`: Focuses on single-process, deterministic scheduling loops, deterministic due-time sorting, and DAGs.
- `v2-extended`: Extends triggers and comprehensive retry backoff logic mapping specific task-level profiles.
- `v3-optimized`: Introduces explicit completion barriers for multi-node dependency aggregation and bounded concurrency limits maximizing throughput."
