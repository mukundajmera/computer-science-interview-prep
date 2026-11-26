import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Locker {
    private final List<Compartment> compartments;
    private final Map<String, AccessToken> tokens;
    private final Clock clock;
    private final Duration tokenTtl;
    private long tokenCounter;

    public Locker(int smallCount, int mediumCount, int largeCount) {
        this(smallCount, mediumCount, largeCount, Clock.systemUTC(), Duration.ofDays(7));
    }

    public Locker(int smallCount, int mediumCount, int largeCount, Clock clock, Duration tokenTtl) {
        this.compartments = new ArrayList<>();
        this.tokens = new HashMap<>();
        this.clock = clock.withZone(ZoneOffset.UTC);
        this.tokenTtl = tokenTtl;
        this.tokenCounter = 0;
        initCompartments(smallCount, mediumCount, largeCount);
    }

    public String depositPackage(PackageSize size) {
        Compartment compartment = findExactAvailable(size);
        if (compartment == null) {
            return null;
        }

        compartment.markOccupied();
        String tokenCode = "T-" + (++tokenCounter);
        AccessToken token = new AccessToken(tokenCode, compartment.getId(), Instant.now(clock).plus(tokenTtl));
        tokens.put(tokenCode, token);
        return tokenCode;
    }

    public boolean pickup(String tokenCode) {
        AccessToken token = tokens.get(tokenCode);
        if (token == null) {
            return false;
        }
        if (token.isExpired(Instant.now(clock))) {
            return false;
        }

        Compartment compartment = findById(token.getCompartmentId());
        if (compartment == null) {
            return false;
        }

        compartment.markAvailable();
        tokens.remove(tokenCode);
        return true;
    }

    public boolean pickupPackage(String tokenCode) {
        return pickup(tokenCode);
    }

    public int clearExpiredDeposits() {
        int cleared = 0;
        Instant now = Instant.now(clock);
        List<String> expiredCodes = new ArrayList<>();
        for (Map.Entry<String, AccessToken> entry : tokens.entrySet()) {
            if (entry.getValue().isExpired(now)) {
                expiredCodes.add(entry.getKey());
            }
        }

        for (String code : expiredCodes) {
            AccessToken token = tokens.remove(code);
            Compartment compartment = findById(token.getCompartmentId());
            if (compartment != null) {
                compartment.markAvailable();
                cleared++;
            }
        }

        return cleared;
    }

    public int getActiveTokenCount() {
        return tokens.size();
    }

    private Compartment findExactAvailable(PackageSize size) {
        for (Compartment compartment : compartments) {
            if (compartment.getSize() == size && compartment.isAvailable()) {
                return compartment;
            }
        }
        return null;
    }

    private Compartment findById(String id) {
        for (Compartment compartment : compartments) {
            if (compartment.getId().equals(id)) {
                return compartment;
            }
        }
        return null;
    }

    private void initCompartments(int smallCount, int mediumCount, int largeCount) {
        for (int i = 1; i <= smallCount; i++) {
            compartments.add(new Compartment("S-" + i, PackageSize.SMALL));
        }
        for (int i = 1; i <= mediumCount; i++) {
            compartments.add(new Compartment("M-" + i, PackageSize.MEDIUM));
        }
        for (int i = 1; i <= largeCount; i++) {
            compartments.add(new Compartment("L-" + i, PackageSize.LARGE));
        }
    }
}
