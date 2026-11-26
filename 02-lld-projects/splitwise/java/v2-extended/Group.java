import java.util.*;

/**
 * Splitwise - V2 Extended
 * 
 * Group for shared expenses among a set of users.
 */
public class Group {
    private final String id;
    private final String name;
    private final List<User> members;
    private final List<Expense> expenses;

    public Group(String id, String name) {
        this.id = id;
        this.name = name;
        this.members = new ArrayList<>();
        this.expenses = new ArrayList<>();
    }

    public String getId() { return id; }
    public String getName() { return name; }

    public void addMember(User user) {
        if (!members.contains(user)) {
            members.add(user);
        }
    }

    public void removeMember(User user) {
        members.remove(user);
    }

    public List<User> getMembers() {
        return new ArrayList<>(members);
    }

    public void addExpense(Expense expense) {
        expenses.add(expense);
    }

    public List<Expense> getExpenses() {
        return new ArrayList<>(expenses);
    }

    @Override
    public String toString() {
        return String.format("Group '%s' (%d members)", name, members.size());
    }
}
