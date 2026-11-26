package v3_optimized;

import java.util.HashSet;
import java.util.Set;

public class FingerprintStore {
    private final Set<String> fingerprints = new HashSet<>();
    private final Set<String> bloomFilter = new HashSet<>();

    public synchronized boolean add(String fingerprint) {
        String bloomHash = String.valueOf(Math.abs(fingerprint.hashCode()));
        if (bloomFilter.contains(bloomHash)) {
            if (fingerprints.contains(fingerprint)) {
                return false;
            }
            fingerprints.add(fingerprint);
            return true;
        }
        
        bloomFilter.add(bloomHash);
        fingerprints.add(fingerprint);
        return true;
    }
}
