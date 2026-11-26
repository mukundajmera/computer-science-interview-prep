# ATM System — Follow-Up Questions

Use these variants to drive deeper interview discussion after the baseline design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you handle a network partition during a dispense?
- **Model Answer**: Implement a resilient timeout and compensating transaction mechanism. The ATM should only dispense physical cash if it receives a definitive success from the bank. If a timeout occurs, it must initiate a rollback.

## 2. How to design the cash dispenser algorithm (Chain of Responsibility)?
- **Model Answer**: Use a chain of processors, each handling a specific denomination (e.g., $100 -> $50 -> $20). Each processor dispenses what it can and passes the remainder to the next.

## 3. How would you handle multiple currencies?
- **Model Answer**: Add currency types to the Account and ATM configurations. Implement a real-time exchange rate service dependency for cross-currency withdrawals.

## 4. How to scale the central banking system handling millions of ATMs?
- **Model Answer**: Use stateless microservices behind load balancers. Partition the account database (sharding by Account ID) and use caching for read-heavy operations like balance checks.

## 5. How would you implement card capture logic?
- **Model Answer**: Add a 'CaptureCard' state. Trigger it based on a configurable policy (e.g., 3 failed PIN attempts, expired card, or stolen card signal from the bank).

## 6. How do you handle hardware failure mid-transaction?
- **Model Answer**: Rely on the transaction log. The system should be able to recover its state on reboot and execute compensating transactions for any incomplete operations found in the log.

## 7. How to manage ATM cash replenishment scheduling?
- **Model Answer**: Implement an asynchronous event stream that emits current cash levels. A central routing service consumes this to optimize armored truck routes dynamically.

## 8. What is your strategy for updating ATM software?
- **Model Answer**: Support over-the-air (OTA) updates using blue-green deployments on the device. Ensure the update only runs when the ATM is strictly in the 'Idle' state.

## 9. How to ensure idempotency for withdrawal retries?
- **Model Answer**: The ATM must generate a unique Transaction ID for the session. The bank backend checks this ID; if seen before, it returns the cached result rather than deducting funds again.

## 10. How would you handle check deposits (with image processing)?
- **Model Answer**: Add a CheckScanner hardware interface. The ATM captures the image, performs local OCR for amount extraction, and uploads the image asynchronously to a central clearinghouse service.

---

## Follow-Up Scoring Signals

1. Candidate explains trade-offs, not only feature lists.
2. Candidate preserves API boundaries while extending behavior.
3. Candidate keeps concurrency and safety constraints explicit.
