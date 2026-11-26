public class Player {
    private final String name;
    private final BlackjackHand hand;
    private int balance;
    private int currentBet;

    public Player(String name, int startingBalance) {
        this.name = name;
        this.balance = startingBalance;
        this.hand = new BlackjackHand();
        this.currentBet = 0;
    }

    public String getName() {
        return name;
    }

    public BlackjackHand getHand() {
        return hand;
    }

    public int getBalance() {
        return balance;
    }

    public void placeBet(int amount) {
        if (amount > balance) {
            throw new IllegalArgumentException("Insufficient balance.");
        }
        this.currentBet = amount;
        this.balance -= amount;
    }

    public void doubleBet() {
        if (currentBet > balance) {
            throw new IllegalArgumentException("Insufficient balance to double down.");
        }
        this.balance -= this.currentBet;
        this.currentBet *= 2;
    }

    public void receiveWinnings(double multiplier) {
        this.balance += (int) (this.currentBet * multiplier);
    }

    public void pushBet() {
        this.balance += this.currentBet;
    }

    public void resetBet() {
        this.currentBet = 0;
    }
}
