import enums.TransactionType;
import models.Account;
import models.Card;
import models.Transaction;
import java.util.ArrayList;
import java.util.List;

/**
 * ATM.java - Main ATM machine controller.
 * 
 * DESIGN PATTERNS:
 * - State Pattern (implicit): Different behaviors based on card/auth state
 * - In v2: Explicit ATMState interface
 * 
 * FLOW:
 * 1. insertCard() → Card inserted
 * 2. authenticatePin() → User authenticated
 * 3. checkBalance() / withdraw() / deposit() → Operations
 * 4. ejectCard() → Session end
 * 
 * INTERVIEW TIP: Discuss State Pattern for ATM states.
 */
public class ATM {
    private final String atmId;
    private final String location;
    private Card currentCard;
    private boolean isAuthenticated;
    private final List<Transaction> transactionLog;

    public ATM(String atmId, String location) {
        this.atmId = atmId;
        this.location = location;
        this.currentCard = null;
        this.isAuthenticated = false;
        this.transactionLog = new ArrayList<>();
    }

    /**
     * Insert card into ATM.
     */
    public boolean insertCard(Card card) {
        if (currentCard != null) {
            System.out.println("Another card is already inserted");
            return false;
        }
        currentCard = card;
        System.out.println("Card inserted: " + card.getMaskedNumber());
        return true;
    }

    /**
     * Authenticate user with PIN.
     * Ejects card if account gets locked.
     */
    public boolean authenticatePin(String pin) {
        if (currentCard == null) {
            System.out.println("Please insert a card first");
            return false;
        }

        Account account = currentCard.getLinkedAccount();
        if (account.isLocked()) {
            System.out.println("Account is locked. Please contact bank.");
            ejectCard();
            return false;
        }

        if (account.validatePin(pin)) {
            isAuthenticated = true;
            System.out.println("Authentication successful!");
            return true;
        } else {
            System.out.println("Invalid PIN");
            if (account.isLocked()) {
                ejectCard();
            }
            return false;
        }
    }

    /**
     * Check account balance.
     */
    public void checkBalance() {
        if (!isAuthenticated) {
            System.out.println("Please authenticate first");
            return;
        }
        Transaction transaction = new Transaction(
                TransactionType.BALANCE_INQUIRY, 0, currentCard.getLinkedAccount());
        transaction.execute();
        transactionLog.add(transaction);
    }

    /**
     * Withdraw cash from account.
     */
    public boolean withdraw(double amount) {
        if (!isAuthenticated) {
            System.out.println("Please authenticate first");
            return false;
        }
        Transaction transaction = new Transaction(
                TransactionType.WITHDRAWAL, amount, currentCard.getLinkedAccount());
        boolean success = transaction.execute();
        transactionLog.add(transaction);
        return success;
    }

    /**
     * Deposit cash to account.
     */
    public boolean deposit(double amount) {
        if (!isAuthenticated) {
            System.out.println("Please authenticate first");
            return false;
        }
        Transaction transaction = new Transaction(
                TransactionType.DEPOSIT, amount, currentCard.getLinkedAccount());
        boolean success = transaction.execute();
        transactionLog.add(transaction);
        return success;
    }

    /**
     * Eject card and end session.
     */
    public void ejectCard() {
        if (currentCard != null) {
            System.out.println("Card ejected: " + currentCard.getMaskedNumber());
            currentCard = null;
            isAuthenticated = false;
        }
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

    public String getLocation() {
        return location;
    }
}
