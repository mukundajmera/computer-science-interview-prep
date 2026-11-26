/**
 * Splitwise - V1 Basic
 * 
 * Split classes representing how an expense is divided.
 */
public abstract class Split {
    protected User user;

    public Split(User user) {
        this.user = user;
    }

    public User getUser() {
        return user;
    }

    public abstract double getAmount();
}

/**
 * Equal split - amount calculated based on total and participant count.
 */
class EqualSplit extends Split {
    private double amount;

    public EqualSplit(User user) {
        super(user);
    }

    public void setAmount(double amount) {
        this.amount = amount;
    }

    @Override
    public double getAmount() {
        return amount;
    }
}
