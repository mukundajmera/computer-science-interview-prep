import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.Collections;

public class DoubleEntryLedgerV2 {
    public enum EntryType { DEBIT, CREDIT }

    public static class LedgerEntry {
        public final String entryId;
        public final String transactionId;
        public final String accountId;
        public final EntryType entryType;
        public final BigDecimal amount;
        public final String currency;
        public final Instant createdAt;

        public LedgerEntry(String transactionId, String accountId, EntryType entryType, BigDecimal amount, String currency) {
            this.entryId = UUID.randomUUID().toString();
            this.transactionId = transactionId;
            this.accountId = accountId;
            this.entryType = entryType;
            this.amount = amount;
            this.currency = currency;
            this.createdAt = Instant.now();
        }
    }

    private final List<LedgerEntry> journal = new ArrayList<>();

    public synchronized void commitTransaction(List<LedgerEntry> entries) {
        BigDecimal totalDebit = BigDecimal.ZERO;
        BigDecimal totalCredit = BigDecimal.ZERO;

        for (LedgerEntry entry : entries) {
            if (entry.entryType == EntryType.DEBIT) {
                totalDebit = totalDebit.add(entry.amount);
            } else if (entry.entryType == EntryType.CREDIT) {
                totalCredit = totalCredit.add(entry.amount);
            }
        }

        if (totalDebit.compareTo(totalCredit) != 0) {
            throw new IllegalStateException("Double-entry invariant violated: Debits (" + totalDebit + ") do not equal Credits (" + totalCredit + ")");
        }

        journal.addAll(entries);
    }

    public synchronized List<LedgerEntry> getJournal() {
        return Collections.unmodifiableList(new ArrayList<>(journal));
    }
}
