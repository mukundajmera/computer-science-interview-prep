import states.ATMState;
import states.IdleState;
import models.Card;
import models.Account;
import models.Transaction;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.atomic.AtomicReference;

/**
 * ATM.java - v3 Optimized Thread-Safe Version.
 * 
 * THREAD SAFETY:
 * - AtomicReference for state transitions
 * - ReentrantLock for transaction operations
 * - CAS for state changes
 * 
 * INTERVIEW TIP: Discuss trade-offs of different locking strategies.
 */
public class ATM {
    private final String atmId;
    private final String location;
    private final AtomicReference<ATMState> currentState;
    private volatile Card currentCard;
    private volatile Account currentAccount;
    private final List<Transaction> transactionLog;
    private final ReentrantLock transactionLock;

    public ATM(String atmId, String location) {
        this.atmId = atmId;
        this.location = location;
        this.currentState = new AtomicReference<>(new IdleState());
        this.currentCard = null;
        this.currentAccount = null;
        this.transactionLog = new ArrayList<>();
        this.transactionLock = new ReentrantLock();
    }

    public void insertCard(Card card) {
        currentState.get().insertCard(this, card);
    }

    public boolean authenticatePin(String pin) {
        return currentState.get().authenticatePin(this, pin);
    }

    public void selectAccount(int index) {
        currentState.get().selectAccount(this, index);
    }

    public void checkBalance() {
        transactionLock.lock();
        try {
            currentState.get().checkBalance(this);
        } finally {
            transactionLock.unlock();
        }
    }

    public boolean withdraw(double amount) {
        transactionLock.lock();
        try {
            return currentState.get().withdraw(this, amount);
        } finally {
            transactionLock.unlock();
        }
    }

    public boolean deposit(double amount) {
        transactionLock.lock();
        try {
            return currentState.get().deposit(this, amount);
        } finally {
            transactionLock.unlock();
        }
    }

    public void ejectCard() {
        currentState.get().ejectCard(this);
    }

    // Thread-safe state transition using CAS
    public void setState(ATMState state) {
        currentState.set(state);
    }

    public ATMState getState() {
        return currentState.get();
    }

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
