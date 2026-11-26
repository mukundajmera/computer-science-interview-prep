
public class DeliveryResult {
    private final int statusCode;
    private final boolean success;

    public DeliveryResult(int statusCode, boolean success) {
        this.statusCode = statusCode;
        this.success = success;
    }

    public int getStatusCode() { return statusCode; }
    public boolean isSuccess() { return success; }
}
