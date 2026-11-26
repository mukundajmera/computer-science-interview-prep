import java.util.List;
import java.util.ArrayList;
import java.util.UUID;

/**
 * Splitwise - V1 Basic
 * 
 * Expense class representing a single expense.
 */
public class Expense {
    private final String id;
    private final String description;
    private final double amount;
    private final User paidBy;
    private final List<Split> splits;

    private Expense(String id, String description, double amount, User paidBy, List<Split> splits) {
        this.id = id;
        this.description = description;
        this.amount = amount;
        this.paidBy = paidBy;
        this.splits = splits;
    }

    public String getId() { return id; }
    public String getDescription() { return description; }
    public double getAmount() { return amount; }
    public User getPaidBy() { return paidBy; }
    public List<Split> getSplits() { return splits; }

    /**
     * Create an expense with equal split among participants.
     */
    public static Expense createEqualExpense(String description, double amount, 
                                              User paidBy, List<User> participants) {
        List<Split> splits = new ArrayList<>();
        double splitAmount = amount / participants.size();
        
        // Handle rounding
        double roundedAmount = Math.round(splitAmount * 100.0) / 100.0;
        double total = roundedAmount * participants.size();
        double diff = amount - total;
        
        boolean firstDone = false;
        for (User user : participants) {
            EqualSplit split = new EqualSplit(user);
            if (!firstDone && Math.abs(diff) > 0.001) {
                split.setAmount(roundedAmount + diff);
                firstDone = true;
            } else {
                split.setAmount(roundedAmount);
            }
            splits.add(split);
        }

        return new Expense(UUID.randomUUID().toString(), description, amount, paidBy, splits);
    }

    @Override
    public String toString() {
        return String.format("%s paid $%.2f for '%s'", paidBy.getName(), amount, description);
    }
}
