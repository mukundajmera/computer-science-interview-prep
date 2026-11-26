import java.util.List;

/**
 * Splitwise - V1 Basic Demo
 */
public class SplitwiseDemo {

    public static void main(String[] args) {
        System.out.println("=== Splitwise Demo ===\n");

        ExpenseManager manager = new ExpenseManager();

        // Create users
        User alice = new User("1", "Alice", "alice@email.com");
        User bob = new User("2", "Bob", "bob@email.com");
        User charlie = new User("3", "Charlie", "charlie@email.com");

        manager.addUser(alice);
        manager.addUser(bob);
        manager.addUser(charlie);

        System.out.println("Users added: Alice, Bob, Charlie\n");

        // Expense 1: Alice pays $300 for dinner, split equally
        System.out.println("--- Expense 1 ---");
        Expense dinner = Expense.createEqualExpense(
            "Dinner at restaurant",
            300.0,
            alice,
            List.of(alice, bob, charlie)
        );
        manager.addExpense(dinner);
        System.out.println(dinner);
        System.out.println("Split: $100 each");

        // Expense 2: Bob pays $150 for movie, split equally
        System.out.println("\n--- Expense 2 ---");
        Expense movie = Expense.createEqualExpense(
            "Movie tickets",
            150.0,
            bob,
            List.of(alice, bob, charlie)
        );
        manager.addExpense(movie);
        System.out.println(movie);
        System.out.println("Split: $50 each");

        // Show balances
        System.out.println("\n--- Current Balances ---");
        manager.showBalances();

        // Expense 3: Charlie pays $90 for groceries
        System.out.println("\n--- Expense 3 ---");
        Expense groceries = Expense.createEqualExpense(
            "Groceries",
            90.0,
            charlie,
            List.of(alice, bob, charlie)
        );
        manager.addExpense(groceries);
        System.out.println(groceries);

        // Final balances
        System.out.println("\n--- Final Balances ---");
        manager.showBalances();

        // Show Alice's balance
        System.out.println("\n--- Alice's Balance Summary ---");
        var aliceBalances = manager.getBalance(alice.getId());
        for (var entry : aliceBalances.entrySet()) {
            User other = manager.getUser(entry.getKey());
            double amount = entry.getValue();
            if (amount > 0) {
                System.out.printf("Alice owes %s: $%.2f%n", other.getName(), amount);
            } else {
                System.out.printf("%s owes Alice: $%.2f%n", other.getName(), -amount);
            }
        }

        System.out.println("\n=== Demo Complete ===");
    }
}
