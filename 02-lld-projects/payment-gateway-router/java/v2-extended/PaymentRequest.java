
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
public class PaymentRequest {
    private final String id;
    private final String idempotencyKey;
    private final double amount;
    private final String currency;
    private final String userId;

    public PaymentRequest(String id, String idempotencyKey, double amount, String currency, String userId) {
        this.id = id;
        this.idempotencyKey = idempotencyKey;
        this.amount = amount;
        this.currency = currency;
        this.userId = userId;
    }

    public String getId() { return id; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public String getUserId() { return userId; }
}
