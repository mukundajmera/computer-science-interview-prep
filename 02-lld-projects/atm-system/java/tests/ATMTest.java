/**
 * ATM System Tests - JUnit 5
 * 
 * Tests for all versions of the ATM system
 */

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.function.Executable;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// ==================== Test Enums ====================

enum AccountType {
    CHECKING, SAVINGS
}

enum TransactionType {
    BALANCE_INQUIRY, WITHDRAWAL, DEPOSIT
}

enum TransactionStatus {
    PENDING, COMPLETED, FAILED
}

// ==================== Minimal Account for Testing ====================

class Account {
    private final String accountNumber;
    private final AccountType accountType;
    private double balance;
    private String pin;
    private boolean isLocked;
    private int failedAttempts;
    private final ReentrantLock lock = new ReentrantLock();
    
    private static final int MAX_FAILED_ATTEMPTS = 3;
    
    public Account(String accountNumber, AccountType accountType, double initialBalance, String pin) {
        this.accountNumber = accountNumber;
        this.accountType = accountType;
        this.balance = initialBalance;
        this.pin = pin;
        this.isLocked = false;
        this.failedAttempts = 0;
    }
    
    public String getAccountNumber() { return accountNumber; }
    public AccountType getAccountType() { return accountType; }
    public double getBalance() { 
        lock.lock();
        try {
            return balance; 
        } finally {
            lock.unlock();
        }
    }
    public boolean isLocked() { return isLocked; }
    
    public boolean validatePin(String inputPin) {
        if (isLocked) return false;
        
        if (pin.equals(inputPin)) {
            failedAttempts = 0;
            return true;
        } else {
            failedAttempts++;
            if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
                isLocked = true;
            }
            return false;
        }
    }
    
    public boolean withdraw(double amount) {
        lock.lock();
        try {
            if (amount <= 0 || amount > balance) return false;
            balance -= amount;
            return true;
        } finally {
            lock.unlock();
        }
    }
    
    public boolean deposit(double amount) {
        lock.lock();
        try {
            if (amount <= 0) return false;
            balance += amount;
            return true;
        } finally {
            lock.unlock();
        }
    }
    
    public ReentrantLock getLock() {
        return lock;
    }
    
    public static boolean transferBetweenAccounts(Account from, Account to, double amount) {
        if (amount <= 0) return false;
        
        int hash1 = from.getAccountNumber().hashCode();
        int hash2 = to.getAccountNumber().hashCode();
        Account first = hash1 < hash2 ? from : to;
        Account second = first == from ? to : from;
        if (hash1 == hash2) {
            first = from.getAccountNumber().compareTo(to.getAccountNumber()) < 0 ? from : to;
            second = first == from ? to : from;
        }
        
        first.getLock().lock();
        try {
            second.getLock().lock();
            try {
                if (from.balance < amount) return false;
                from.balance -= amount;
                to.balance += amount;
                return true;
            } finally {
                second.getLock().unlock();
            }
        } finally {
            first.getLock().unlock();
        }
    }
}

class Card {
    private final String cardNumber;
    private final Account linkedAccount;
    
    public Card(String cardNumber, Account linkedAccount) {
        this.cardNumber = cardNumber;
        this.linkedAccount = linkedAccount;
    }
    
    public String getCardNumber() { return cardNumber; }
    public Account getLinkedAccount() { return linkedAccount; }
    public String getMaskedNumber() {
        return "XXXX-XXXX-XXXX-" + cardNumber.substring(cardNumber.length() - 4);
    }
}

// ==================== Tests ====================

public class ATMTest {
    
    private Account testAccount;
    private Card testCard;
    
    @BeforeEach
    void setUp() {
        testAccount = new Account("ACC001", AccountType.CHECKING, 1000.0, "1234");
        testCard = new Card("1234567890123456", testAccount);
    }
    
    // ==================== Account Tests ====================
    
    @Nested
    @DisplayName("Account Tests")
    class AccountTests {
        
        @Test
        @DisplayName("Account creation with valid data")
        void testAccountCreation() {
            assertNotNull(testAccount);
            assertEquals("ACC001", testAccount.getAccountNumber());
            assertEquals(AccountType.CHECKING, testAccount.getAccountType());
            assertEquals(1000.0, testAccount.getBalance());
            assertFalse(testAccount.isLocked());
        }
        
        @Test
        @DisplayName("PIN validation - correct PIN")
        void testValidPinAuthentication() {
            assertTrue(testAccount.validatePin("1234"));
        }
        
        @Test
        @DisplayName("PIN validation - incorrect PIN")
        void testInvalidPinAuthentication() {
            assertFalse(testAccount.validatePin("0000"));
            assertFalse(testAccount.isLocked());
        }
        
        @Test
        @DisplayName("Account locks after 3 failed attempts")
        void testAccountLockAfterFailedAttempts() {
            testAccount.validatePin("0000"); // 1st failed
            testAccount.validatePin("1111"); // 2nd failed
            assertFalse(testAccount.isLocked());
            testAccount.validatePin("2222"); // 3rd failed - should lock
            assertTrue(testAccount.isLocked());
        }
        
        @Test
        @DisplayName("Locked account cannot authenticate")
        void testLockedAccountCannotAuthenticate() {
            // Lock the account
            testAccount.validatePin("0000");
            testAccount.validatePin("1111");
            testAccount.validatePin("2222");
            
            // Even correct PIN should fail
            assertFalse(testAccount.validatePin("1234"));
        }
        
        @Test
        @DisplayName("Successful withdrawal")
        void testSuccessfulWithdrawal() {
            assertTrue(testAccount.withdraw(200));
            assertEquals(800.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Withdrawal fails for insufficient balance")
        void testWithdrawalInsufficientBalance() {
            assertFalse(testAccount.withdraw(1500));
            assertEquals(1000.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Withdrawal fails for invalid amount")
        void testWithdrawalInvalidAmount() {
            assertFalse(testAccount.withdraw(-50));
            assertFalse(testAccount.withdraw(0));
            assertEquals(1000.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Successful deposit")
        void testSuccessfulDeposit() {
            assertTrue(testAccount.deposit(500));
            assertEquals(1500.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Deposit fails for invalid amount")
        void testDepositInvalidAmount() {
            assertFalse(testAccount.deposit(-50));
            assertFalse(testAccount.deposit(0));
            assertEquals(1000.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Multiple transactions")
        void testMultipleTransactions() {
            testAccount.withdraw(200);
            testAccount.deposit(150);
            testAccount.withdraw(100);
            
            assertEquals(850.0, testAccount.getBalance());
        }
    }
    
    // ==================== Card Tests ====================
    
    @Nested
    @DisplayName("Card Tests")
    class CardTests {
        
        @Test
        @DisplayName("Card creation and masking")
        void testCardCreation() {
            assertEquals("XXXX-XXXX-XXXX-3456", testCard.getMaskedNumber());
            assertEquals(testAccount, testCard.getLinkedAccount());
        }
        
        @Test
        @DisplayName("Card links to correct account")
        void testCardAccountLink() {
            Account linkedAccount = testCard.getLinkedAccount();
            assertEquals("ACC001", linkedAccount.getAccountNumber());
        }
    }
    
    // ==================== Integration Tests ====================
    
    @Nested
    @DisplayName("Integration Tests")
    class IntegrationTests {
        
        @Test
        @DisplayName("Complete withdrawal flow")
        void testCompleteWithdrawalFlow() {
            // Authenticate
            assertTrue(testAccount.validatePin("1234"));
            
            // Check initial balance
            assertEquals(1000.0, testAccount.getBalance());
            
            // Withdraw
            assertTrue(testAccount.withdraw(300));
            assertEquals(700.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Complete deposit flow")
        void testCompleteDepositFlow() {
            // Authenticate
            assertTrue(testAccount.validatePin("1234"));
            
            // Deposit
            assertTrue(testAccount.deposit(500));
            assertEquals(1500.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Failed authentication blocks transactions")
        void testFailedAuthBlocksTransactions() {
            // Lock account
            testAccount.validatePin("0000");
            testAccount.validatePin("1111");
            testAccount.validatePin("2222");
            
            // Account should be locked
            assertTrue(testAccount.isLocked());
            
            // Cannot authenticate even with correct PIN
            assertFalse(testAccount.validatePin("1234"));
        }
        
        @Test
        @DisplayName("Edge case: Withdraw exact balance")
        void testWithdrawExactBalance() {
            assertTrue(testAccount.withdraw(1000.0));
            assertEquals(0.0, testAccount.getBalance());
        }
        
        @Test
        @DisplayName("Edge case: Small deposit and withdrawal")
        void testSmallAmounts() {
            assertTrue(testAccount.deposit(0.01));
            assertEquals(1000.01, testAccount.getBalance(), 0.001);
            
            assertTrue(testAccount.withdraw(0.01));
            assertEquals(1000.0, testAccount.getBalance(), 0.001);
        }
    }
    
    // ==================== Concurrent Tests ====================
    
    @Nested
    @DisplayName("Concurrent Tests")
    class ConcurrentTests {
        @Test
        @DisplayName("Concurrent transfers between accounts")
        void testConcurrentTransfers() throws InterruptedException {
            Account acc1 = new Account("ACC1", AccountType.CHECKING, 1000.0, "1234");
            Account acc2 = new Account("ACC2", AccountType.CHECKING, 1000.0, "5678");
            
            int numThreads = 8;
            int iterations = 100;
            ExecutorService executor = Executors.newFixedThreadPool(numThreads);
            CountDownLatch latch = new CountDownLatch(numThreads);
            
            for (int i = 0; i < numThreads / 2; i++) {
                executor.submit(() -> {
                    for (int j = 0; j < iterations; j++) {
                        Account.transferBetweenAccounts(acc1, acc2, 10.0);
                    }
                    latch.countDown();
                });
                executor.submit(() -> {
                    for (int j = 0; j < iterations; j++) {
                        Account.transferBetweenAccounts(acc2, acc1, 10.0);
                    }
                    latch.countDown();
                });
            }
            
            latch.await();
            executor.shutdown();
            
            assertEquals(1000.0, acc1.getBalance());
            assertEquals(1000.0, acc2.getBalance());
        }
    }
    
    // ==================== Boundary Tests ====================
    
    @Nested
    @DisplayName("Boundary Tests")
    class BoundaryTests {
        
        @Test
        @DisplayName("PIN reset after successful auth")
        void testPinResetAfterSuccess() {
            // Two failed attempts
            testAccount.validatePin("0000");
            testAccount.validatePin("1111");
            
            // Successful attempt should reset counter
            assertTrue(testAccount.validatePin("1234"));
            
            // Two more failed attempts
            testAccount.validatePin("0000");
            testAccount.validatePin("1111");
            
            // Account should NOT be locked
            assertFalse(testAccount.isLocked());
        }
        
        @Test
        @DisplayName("Different account types")
        void testDifferentAccountTypes() {
            Account savings = new Account("SAV001", AccountType.SAVINGS, 5000.0, "5678");
            assertEquals(AccountType.SAVINGS, savings.getAccountType());
            assertEquals(5000.0, savings.getBalance());
        }
    }
    
    // ==================== Main method for running tests ====================
    
    public static void main(String[] args) {
        System.out.println("Running ATM System Tests...\n");
        
        // Run tests manually for demonstration
        ATMTest test = new ATMTest();
        int passed = 0;
        int failed = 0;
        
        // Account Tests
        try {
            test.setUp();
            test.new AccountTests().testAccountCreation();
            System.out.println("✓ Account creation test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Account creation test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new AccountTests().testValidPinAuthentication();
            System.out.println("✓ Valid PIN authentication test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Valid PIN authentication test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new AccountTests().testSuccessfulWithdrawal();
            System.out.println("✓ Successful withdrawal test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Successful withdrawal test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new AccountTests().testSuccessfulDeposit();
            System.out.println("✓ Successful deposit test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Successful deposit test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new AccountTests().testAccountLockAfterFailedAttempts();
            System.out.println("✓ Account lock test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Account lock test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new IntegrationTests().testCompleteWithdrawalFlow();
            System.out.println("✓ Complete withdrawal flow test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Complete withdrawal flow test failed: " + e.getMessage());
            failed++;
        }
        
        System.out.println("\n=== Test Results ===");
        System.out.println("Passed: " + passed);
        System.out.println("Failed: " + failed);
        System.out.println("Total: " + (passed + failed));
    }
}
