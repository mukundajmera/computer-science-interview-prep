import states.ATMState;
import states.IdleState;
import models.Card;
import models.Account;
import models.Transaction;
import java.util.ArrayList;
import java.util.List;

/**
 * ATM.java - v2 Extended with State Pattern.
 * 
 * DESIGN PATTERNS:
 * - State Pattern: Delegates behavior to current ATMState
 * - Command Pattern: Transactions are commands with execute()
 * 
 * INTERVIEW TIP: State Pattern eliminates complex if-else chains.
 */
public class ATM {
    private final String atmId;
    private final String location;
    private ATMState currentState;
    private Card currentCard;
    private Account currentAccount;
    private final List<Transaction> transactionLog;

    public ATM(String atmId, String location) {
        this.atmId = atmId;
        this.location = location;
        this.currentState = new IdleState();
        this.currentCard = null;
        this.currentAccount = null;
        this.transactionLog = new ArrayList<>();
    }

    // Delegate all operations to current state
    public void insertCard(Card card) {
        currentState.insertCard(this, card);
    }

    public boolean authenticatePin(String pin) {
        return currentState.authenticatePin(this, pin);
    }

    public void selectAccount(int index) {
        currentState.selectAccount(this, index);
    }

    public void checkBalance() {
        currentState.checkBalance(this);
    }

    public boolean withdraw(double amount) {
        return currentState.withdraw(this, amount);
    }

    public boolean deposit(double amount) {
        return currentState.deposit(this, amount);
    }

    public void ejectCard() {
        currentState.ejectCard(this);
    }

    // State management (called by states)
    public void setState(ATMState state) {
        this.currentState = state;
    }

    public ATMState getState() {
        return currentState;
    }

    // Card/Account management (called by states)
    public void setCurrentCard(Card card) {
        this.currentCard = card;
    }

    public Card getCurrentCard() {
        return currentCard;
    }

    public void setCurrentAccount(Account account) {
        this.currentAccount = account;
    }

    public Account getCurrentAccount() {
        return currentAccount;
    }

    public void addTransaction(Transaction tx) {
        transactionLog.add(tx);
    }

    public void printTransactionLog() {
        System.out.println("\n=== Transaction Log ===");
        for (Transaction t : transactionLog) {
            System.out.println(t);
        }
    }

    public String getAtmId() {
        return atmId;
    }
}
