import java.time.Instant;

public class AccessToken {
    private final String code;
    private final String compartmentId;
    private final Instant expiresAt;

    public AccessToken(String code, String compartmentId, Instant expiresAt) {
        this.code = code;
        this.compartmentId = compartmentId;
        this.expiresAt = expiresAt;
    }

    public String getCode() {
        return code;
    }

    public String getCompartmentId() {
        return compartmentId;
    }

    public Instant getExpiresAt() {
        return expiresAt;
    }

    public boolean isExpired(Instant now) {
        return now.isAfter(expiresAt);
    }
}
