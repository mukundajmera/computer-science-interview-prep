# Interview Questions: Workflow Orchestration

## Basic Questions

### 1. Why do multi-step flows fail more often than single-step APIs?
**A**: They cross service boundaries and time windows, so partial success is common and requires explicit recovery logic.

### 2. What is the main purpose of saga?
**A**: Preserve business consistency across independently committed steps using compensations.

### 3. Why is idempotency mandatory in workflows?
**A**: Retries are unavoidable; without idempotency, retries create duplicate side effects.

## Intermediate Questions

### 4. What should be persisted between steps?
**A**: Workflow ID, current step, step history, retry counters, compensation status, and correlation metadata.

### 5. How do you handle timeout in external dependency calls?
**A**: Fail fast, retry per policy, then compensate or park workflow for manual/action queue depending on criticality.

### 6. Orchestration vs choreography?
**A**: Orchestration centralizes control and observability; choreography reduces central coupling but is harder to reason about globally.

## Advanced Questions

### 7. How do you version workflows safely?
**A**: Keep old definition active for in-flight instances; route new starts to new definition and provide migration rules only where safe.

### 8. How do you design compensation order?
**A**: Reverse execution order for dependent steps, with idempotent compensations and explicit terminal states.

### 9. What metrics matter for workflow health?
**A**: Success ratio, mean completion time, stuck workflow count, compensation rate, retry depth, and dead-letter volume.

## Rapid Follow-up Drill

1. Which checkout step would you never retry blindly?
2. How do you resume after worker restart?
3. What is your dead-letter strategy for terminal failures?
4. How do you expose workflow state to callers?

### 10. How does price tracking use orchestration?
**A**: Treat price changes as workflow triggers: ingest change, evaluate threshold, enqueue notification, and persist delivery outcome with idempotent checkpoints.
