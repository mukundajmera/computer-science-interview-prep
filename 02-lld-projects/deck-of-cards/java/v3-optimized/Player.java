import java.util.ArrayList;
import java.util.List;

public class Player {
    private final String name;
    private double balance;
    private List<BlackjackHand> hands;
    private double insuranceBet;

    public Player(String name, double initialBalance) {
        this.name = name;
        this.balance = initialBalance;
        this.hands = new ArrayList<>();
        this.hands.add(new BlackjackHand());
        this.insuranceBet = 0.0;
    }

    public String getName() {
        return name;
    }

    public double getBalance() {
        return balance;
    }

    public List<BlackjackHand> getHands() {
        return hands;
    }

    public double getInsuranceBet() {
        return insuranceBet;
    }

    public void clearHands() {
        double primaryBet = hands.isEmpty() ? 0.0 : hands.get(0).getBet();
        hands.clear();
        hands.add(new BlackjackHand(primaryBet));
        insuranceBet = 0.0;
    }

    public void placeBet(double amount, int handIndex) {
        if (amount > balance) {
            throw new IllegalArgumentException("Insufficient balance.");
        }
        balance -= amount;
        hands.get(handIndex).addBet(amount);
    }
    
    public void placeInsuranceBet(double amount) {
        if (amount > balance) {
            throw new IllegalArgumentException("Insufficient balance.");
        }
        balance -= amount;
        insuranceBet += amount;
    }
    
    public void winInsurance() {
        balance += insuranceBet * 3; // 2:1 payout + original bet returned
        insuranceBet = 0.0;
    }
    
    public void clearInsuranceBet() {
        insuranceBet = 0.0;
    }

    public void doubleBet(int handIndex) {
        double currentBet = hands.get(handIndex).getBet();
        if (currentBet > balance) {
            throw new IllegalArgumentException("Insufficient balance to double.");
        }
        balance -= currentBet;
        hands.get(handIndex).addBet(currentBet);
    }

    public void receiveWinnings(double multiplier, int handIndex) {
        balance += hands.get(handIndex).getBet() * multiplier;
    }

    public void pushBet(int handIndex) {
        balance += hands.get(handIndex).getBet();
    }
    
    public BlackjackHand addSplitHand(double bet) {
        if (bet > balance) {
            throw new IllegalArgumentException("Insufficient balance for split.");
        }
        balance -= bet;
        BlackjackHand newHand = new BlackjackHand(bet);
        hands.add(newHand);
        return newHand;
    }
}
