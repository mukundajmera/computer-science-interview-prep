import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

public class V1ChecksummedStore {

    private static class Record {
        byte[] data;
        String md5;
        
        Record(byte[] data, String md5) {
            this.data = data;
            this.md5 = md5;
        }
    }

    private final Map<String, Record> metadataIndex = new HashMap<>();

    private String calculateMd5(byte[] data) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(data);
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public void put(String key, byte[] data) {
        metadataIndex.put(key, new Record(data, calculateMd5(data)));
    }

    public byte[] get(String key) {
        Record record = metadataIndex.get(key);
        if (record == null) throw new RuntimeException("Not found");
        
        if (!calculateMd5(record.data).equals(record.md5)) {
            throw new RuntimeException("Bit rot detected for " + key);
        }
        return record.data;
    }

    public void corruptDataForTesting(String key) {
        Record r = metadataIndex.get(key);
        if (r != null && r.data.length > 0) {
            r.data[0] = (byte) (r.data[0] ^ 0xFF);
        }
    }

    public static void main(String[] args) {
        V1ChecksummedStore store = new V1ChecksummedStore();
        String key = "doc.txt";
        store.put(key, "Hello".getBytes());
        
        assert new String(store.get(key)).equals("Hello") : "Get failed";
        
        store.corruptDataForTesting(key);
        boolean caught = false;
        try {
            store.get(key);
        } catch (RuntimeException e) {
            if (e.getMessage().contains("Bit rot")) caught = true;
        }
        assert caught : "Failed to detect bit rot";
        
        System.out.println("V1 Tests Passed!");
    }
}
