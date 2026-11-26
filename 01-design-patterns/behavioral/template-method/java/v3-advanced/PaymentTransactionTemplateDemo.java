package templatemethod.v3;

import java.util.ArrayList;
import java.util.List;

/**
 * v3-advanced: Resilient Financial Transaction Template with Compensation Hooks.
 * Enforces transactional execution invariants:
 * Pre-Authorize -> Fraud Screen (Hook) -> Debit/Transfer -> Post-Audit -> Compensate/Rollback on failure.
 */
public class PaymentTransactionTemplateDemo {

    public static class TransactionResult {
        private final boolean success;
        private final String txnId;
        private final String message;
        private final List<String> auditLogs;

        public TransactionResult(boolean success, String txnId, String message, List<String> auditLogs) {
            this.success = success;
            this.txnId = txnId;
            this.message = message;
            this.auditLogs = new ArrayList<>(auditLogs);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getTxnId() {
            return txnId;
        }

        public String getMessage() {
            return message;
        }

        public List<String> getAuditLogs() {
            return auditLogs;
        }
    }

    public abstract static class PaymentProcessorTemplate {
        private final List<String> logs = new ArrayList<>();

        // The Template Method
        public final TransactionResult processPayment(String txnId, double amount, String currency) {
            logs.clear();
            log("Txn started: " + txnId + " amount: " + amount + " " + currency);

            if (amount <= 0) {
                log("Amount validation failed: " + amount);
                return new TransactionResult(false, txnId, "Invalid amount", logs);
            }

            if (!preAuthorize(txnId, amount)) {
                log("Pre-authorization declined");
                return new TransactionResult(false, txnId, "Pre-auth failed", logs);
            }

            if (requiresFraudCheck() && !passFraudCheck(txnId, amount)) {
                log("Fraud check triggered alert; compensating");
                compensate(txnId, "Flagged by fraud detector");
                return new TransactionResult(false, txnId, "Fraud check failed", logs);
            }

            boolean charged = executeDebit(txnId, amount);
            if (!charged) {
                log("Debit failed; rolling back authorization");
                compensate(txnId, "Debit failure");
                return new TransactionResult(false, txnId, "Payment debit declined", logs);
            }

            recordAuditSuccess(txnId, amount);
            log("Transaction committed successfully");
            return new TransactionResult(true, txnId, "Success", logs);
        }

        protected abstract boolean preAuthorize(String txnId, double amount);
        protected abstract boolean executeDebit(String txnId, double amount);

        // Hooks
        protected boolean requiresFraudCheck() {
            return true;
        }

        protected boolean passFraudCheck(String txnId, double amount) {
            return amount < 10000.0; // flag amounts >= 10,000 by default
        }

        protected void compensate(String txnId, String reason) {
            log("Compensation executed for " + txnId + ": " + reason);
        }

        protected void recordAuditSuccess(String txnId, double amount) {
            log("Audit record stored for " + txnId);
        }

        protected void log(String msg) {
            logs.add(msg);
        }
    }

    public static class CreditCardProcessor extends PaymentProcessorTemplate {
        @Override
        protected boolean preAuthorize(String txnId, double amount) {
            log("Visa/Mastercard pre-auth approved");
            return true;
        }

        @Override
        protected boolean executeDebit(String txnId, double amount) {
            log("Card charged successfully");
            return true;
        }
    }

    public static class HighRiskCryptoProcessor extends PaymentProcessorTemplate {
        private final boolean simulateNetworkDrop;

        public HighRiskCryptoProcessor(boolean simulateNetworkDrop) {
            this.simulateNetworkDrop = simulateNetworkDrop;
        }

        @Override
        protected boolean preAuthorize(String txnId, double amount) {
            log("Wallet signature validated");
            return true;
        }

        @Override
        protected boolean executeDebit(String txnId, double amount) {
            if (simulateNetworkDrop) {
                log("Blockchain node timeout");
                return false;
            }
            log("Gas fee paid and transaction mined");
            return true;
        }

        @Override
        protected boolean requiresFraudCheck() {
            return false; // Permissionless
        }
    }

    public static void main(String[] args) {
        PaymentProcessorTemplate card = new CreditCardProcessor();
        TransactionResult res = card.processPayment("TXN-101", 150.0, "USD");
        System.out.println("Card result: " + res.isSuccess() + " - " + res.getMessage());
    }
}
