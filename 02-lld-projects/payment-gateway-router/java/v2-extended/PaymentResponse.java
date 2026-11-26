
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
public class PaymentResponse {
    public enum Status {
        SUCCESS, FAILED, TIMEOUT, CONFLICT
    }

    private final String transactionId;
    private final Status status;
    private final String message;
    private final String gatewayName;

    public PaymentResponse(String transactionId, Status status, String message, String gatewayName) {
        this.transactionId = transactionId;
        this.status = status;
        this.message = message;
        this.gatewayName = gatewayName;
    }

    public String getTransactionId() { return transactionId; }
    public Status getStatus() { return status; }
    public String getMessage() { return message; }
    public String getGatewayName() { return gatewayName; }
}
