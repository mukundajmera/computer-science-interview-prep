package v2_extended;
import java.util.Set;
import java.util.HashSet;

public class FraudRule {
    private final Set<String> blacklistedUsers = new HashSet<>();

    public FraudRule() {
        blacklistedUsers.add("fraud_user");
    }

    public boolean isFraud(String userId) {
        return blacklistedUsers.contains(userId);
    }
}
