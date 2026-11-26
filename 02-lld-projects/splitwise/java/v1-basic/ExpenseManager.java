import java.util.*;

/**
 * Splitwise - V1 Basic
 * 
 * Main expense manager that tracks users, expenses, and balances.
 */
public class ExpenseManager {
    private final Map<String, User> users;
    private final List<Expense> expenses;
    // balances[debtor][creditor] = amount debtor owes to creditor
    private final Map<String, Map<String, Double>> balances;

    public ExpenseManager() {
        this.users = new HashMap<>();
        this.expenses = new ArrayList<>();
        this.balances = new HashMap<>();
    }

    /**
     * Add a user to the system.
     */
    public void addUser(User user) {
        users.put(user.getId(), user);
        balances.put(user.getId(), new HashMap<>());
    }

    /**
     * Get user by ID.
     */
    public User getUser(String userId) {
        return users.get(userId);
    }

    /**
     * Add an expense and update balances.
     */
    public void addExpense(Expense expense) {
        expenses.add(expense);
        updateBalances(expense);
    }

    /**
     * Update balances based on an expense.
     */
    private void updateBalances(Expense expense) {
        User payer = expense.getPaidBy();

        for (Split split : expense.getSplits()) {
            User borrower = split.getUser();
            double amount = split.getAmount();

            // Skip if payer is the same as borrower
            if (payer.getId().equals(borrower.getId())) {
                continue;
            }

            // Update balance: borrower owes payer
            Map<String, Double> borrowerBalances = balances.get(borrower.getId());
            double currentOwed = borrowerBalances.getOrDefault(payer.getId(), 0.0);
            borrowerBalances.put(payer.getId(), currentOwed + amount);
        }
    }

    /**
     * Get balance for a specific user.
     * Returns map of userId -> amount (positive = owes, negative = owed)
     */
    public Map<String, Double> getBalance(String userId) {
        Map<String, Double> netBalances = new HashMap<>();
        User user = users.get(userId);

        if (user == null) return netBalances;

        // What user owes to others
        Map<String, Double> owes = balances.getOrDefault(userId, new HashMap<>());
        for (Map.Entry<String, Double> entry : owes.entrySet()) {
            String otherUserId = entry.getKey();
            double amount = entry.getValue();
            netBalances.merge(otherUserId, amount, Double::sum);
        }

        // What others owe to user
        for (Map.Entry<String, Map<String, Double>> entry : balances.entrySet()) {
            String otherUserId = entry.getKey();
            if (otherUserId.equals(userId)) continue;

            double owedToUser = entry.getValue().getOrDefault(userId, 0.0);
            if (owedToUser > 0) {
                netBalances.merge(otherUserId, -owedToUser, Double::sum);
            }
        }

        // Remove zero balances
        netBalances.entrySet().removeIf(e -> Math.abs(e.getValue()) < 0.01);

        return netBalances;
    }

    /**
     * Display all non-zero balances.
     */
    public void showBalances() {
        boolean hasBalances = false;

        for (User user : users.values()) {
            Map<String, Double> userBalances = getBalance(user.getId());
            
            for (Map.Entry<String, Double> entry : userBalances.entrySet()) {
                double amount = entry.getValue();
                if (amount > 0.01) {  // User owes money
                    User creditor = users.get(entry.getKey());
                    System.out.printf("%s owes %s: $%.2f%n", 
                        user.getName(), creditor.getName(), amount);
                    hasBalances = true;
                }
            }
        }

        if (!hasBalances) {
            System.out.println("No balances to show - everyone is settled up!");
        }
    }

    /**
     * Get all expenses.
     */
    public List<Expense> getExpenses() {
        return new ArrayList<>(expenses);
    }

    /**
     * Get all users.
     */
    public Collection<User> getUsers() {
        return users.values();
    }
}
