# Strong Answer: Splitwise (Expense Sharing)

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Splitwise (Expense Sharing) system, I will focus on modeling the core entities, defining the interfaces, and ensuring thread-safe operations under high concurrency. I'll begin by outlining the core data models, then progress to the APIs and algorithmic components like debt simplification. Our primary goal is to ensure consistency, accuracy for financial operations, and fault tolerance."

By establishing these constraints early, we frame the discussion around concrete engineering trade-offs. The high-level requirements dictate a system capable of handling substantial load while maintaining precise state transitions for all core domain objects.

### Explicit Clarifications
- **Currency & Precision:** Single currency, rounding exactly to 2 decimal places to avoid floating-point drift.
- **Simplification Constraint:** We will optimize debts periodically or asynchronously to prevent blocking the write path.
- **Scale Boundaries:** Assuming up to 10k users per group, bounded participants list for a single expense transaction.
- **Failures:** Invalid input (e.g., EXACT splits not summing to total, unknown users) must safely rollback without committing any partial ledger mutations.

## 2. Entity Modeling, APIs & Core Components (5-15 minutes)

**Say:** "Let's discuss the entity modeling. The core entities I have identified include `User`, `Expense`, `Split`, and `ExpenseManager`. Each is designed to encapsulate both state and behavior."

### Public APIs
```python
# Python Interface
class ExpenseManager:
    def add_user(self, user: User) -> None
    def add_expense(self, amount: float, description: str, paid_by_id: str, 
                    split_type: SplitType, participant_ids: List[str], 
                    split_details: Optional[List[float]] = None) -> Optional[Expense]
    def get_balance(self, user_id: str) -> Dict[str, float]
    def record_payment(self, from_user_id: str, to_user_id: str, amount: float) -> bool
    def get_simplified_settlements(self) -> List[tuple]
```

```java
// Java Equivalent API
public class ExpenseManager {
    public void addUser(User user);
    public void addExpense(Expense expense);
    public Map<String, Double> getBalance(String userId);
    public void showBalances();
    public List<Expense> getExpenses();
    public Collection<User> getUsers();
}
```

### Version-Specific Feature Deltas
- **v1-basic:** Focuses on pure `EQUAL` splitting and generic balance updates.
- **v2-extended:** Introduces `EXACT` and `PERCENTAGE` splits and `Group` entities.
- **v3-optimized:** Brings in thread-safe operations (`RLock`) and optimized graph simplification. Focused tests target this specific version directory (e.g., executing `pytest test_splitwise.py` directly within `v3-optimized`) to validate current features, explicitly avoiding silent fallbacks that run legacy `v1` tests instead.

## 3. Design Pattern Justifications (15-25 minutes)

**Say:** "In terms of design patterns, I've incorporated the Strategy Pattern for different split methods (equal, exact, percentage). This choice allows for maximum extensibility."

Using Strategy Pattern for different split methods provides us with necessary flexibility. For example, if we need to add a `SHARES` variant to our workflow, we can implement a new class adhering to the `Split` interface without breaking the Open-Closed Principle. This ensures the design remains resilient against changing requirements and enables comprehensive unit testing.

## 4. Correctness, Failure & Concurrency Contracts (25-30 minutes)

**Say:** "Handling concurrency and input correctness is critical. For thread-safety, concurrent expense additions use reentrant locks (`RLock` in Python) on the `ExpenseManager` to serialize balance mutations, preventing lost updates when multiple users add bills simultaneously. Currently in our Java v3 implementation, we rely on standard collections (`HashMap`), assuming a single-threaded environment for simplicity."

### Contract Implementations

These behaviors are implemented and verified in the `v3-optimized` codebase.

**1. Normal Use-Case:** Creating a valid expense updates the internal balance map symmetrically (payer is owed, participants owe).
- **Python:** `self._balance_sheet[split.user.user_id][paid_by.user_id] += split.amount` and `-= split.amount` for the reverse.
- **Java:** `borrowerBalances.put(payer.getId(), currentOwed + amount);`

**2. Empty/Invalid Input:** Rejecting invalid operations cleanly.
- **Python:** Checks `if None in participants: return None` or invalid exact splits (`if not split_details...`).
- **Java:** `if (user == null) return netBalances;` in `getBalance`.

**3. Duplicate Operation:** Generating settlement graphs evaluates idempotently. Repeated calls to calculate simplifications based purely on the current state.
- **Python:** `get_simplified_settlements()` dynamically builds `net_balances = defaultdict(float)` from the current ledger.
- **Java:** Similar stateless balance recalculation using `Map<String, Double> netBalances = new HashMap<>();` inside `getBalance`.

**4. Capacity Boundary:** Memory structures scale efficiently relying on sparse nested mappings rather than a full NxN matrix.
- **Python:** `self._balance_sheet: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))`
- **Java:** `private final Map<String, Map<String, Double>> balances;`

**5. Failure Rollback:** State updates are atomic. If an `EXACT` split sum does not match the total within a 0.01 tolerance, the transaction fails before mutating any ledger state.
- **Python:** Validates before appending: 
  ```python
  if not self._validate_splits(amount, splits):
      return None
  # Only after passing, update balances:
  self._expenses.append(expense)
  self._update_balances(expense)
  ```
- **Java:** Can similarly validate `expense.getSplits()` before committing changes in a more advanced implementation (currently `updateBalances` blindly loops).

## 5. Scaling Limits & Debt Simplification (30-35 minutes)

**Say:** "When we push this system to its scaling limits, the main bottleneck is the debt simplification graph algorithms which can become CPU intensive (O(N) greedy vs O(N!) optimal). We scale this by running graph simplifications asynchronously as batch jobs rather than synchronously on every transaction."

The current algorithm uses a greedy approach combining top debtors with top creditors. As vertical scaling becomes cost-prohibitive, we transition to horizontal partitioning. This introduces complexities like distributed transactions, mitigated using a saga pattern or two-phase commit depending on strictness.

## 6. Indexing Trade-offs (35-40 minutes)

**Say:** "To support efficient queries, we must consider indexing trade-offs. We index heavily on User ID, Group ID, and Expense Date. The trade-off is higher storage costs and slower expense creation."

By carefully selecting compound indexes based on our most frequent query access patterns, we avoid full table scans, though we acknowledge the associated memory overhead and index maintenance penalties during peak write throughput.

## 7. State Synchronization (40-45 minutes)

**Say:** "Finally, state synchronization relies on distributed transactions or saga patterns when payments span different microservices, ensuring that balance deductions and ledger updates remain strictly consistent."

This guarantees that transient network partitions won't compromise the global state of the application, ensuring high availability and fault tolerance across data centers.
