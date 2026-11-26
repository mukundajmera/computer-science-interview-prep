package v2_extended;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.Set;

public class ContentDeduplicator {
    private final Set<String> seenHashes = new HashSet<>();

    public boolean isDuplicate(String content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("MD5");
            byte[] hashBytes = digest.digest(content.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            String hash = sb.toString();
            
            if (seenHashes.contains(hash)) {
                return true;
            }
            seenHashes.add(hash);
            return false;
        } catch (NoSuchAlgorithmException e) {
            return false;
        }
    }
}
