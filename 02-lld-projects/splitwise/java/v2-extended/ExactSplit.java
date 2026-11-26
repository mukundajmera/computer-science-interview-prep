import java.util.*;

/**
 * Splitwise - V2 Extended
 * 
 * Extended split types: Exact and Percentage.
 */

// Base Split class same as v1

/**
 * Exact split - user specifies exact amount they owe.
 */
public class ExactSplit extends Split {
    private final double amount;

    public ExactSplit(User user, double amount) {
        super(user);
        this.amount = amount;
    }

    @Override
    public double getAmount() {
        return amount;
    }
}

/**
 * Percentage split - user owes a percentage of total.
 */
class PercentageSplit extends Split {
    private final double percentage;
    private final double totalAmount;

    public PercentageSplit(User user, double percentage, double totalAmount) {
        super(user);
        this.percentage = percentage;
        this.totalAmount = totalAmount;
    }

    public double getPercentage() {
        return percentage;
    }

    @Override
    public double getAmount() {
        return Math.round((totalAmount * percentage / 100.0) * 100.0) / 100.0;
    }
}

// Abstract Split class (duplicated for compilation)
abstract class Split {
    protected User user;

    public Split(User user) {
        this.user = user;
    }

    public User getUser() {
        return user;
    }

    public abstract double getAmount();
}
