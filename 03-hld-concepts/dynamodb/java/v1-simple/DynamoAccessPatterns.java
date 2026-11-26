import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/**
 * Minimal access-pattern helper that mirrors partition/sort key planning.
 */
public class DynamoAccessPatterns {

    public static final class Key {
        private final String partitionKey;
        private final String sortKey;

        public Key(String partitionKey, String sortKey) {
            this.partitionKey = Objects.requireNonNull(partitionKey, "partitionKey");
            this.sortKey = sortKey;
        }

        public String partitionKey() {
            return partitionKey;
        }

        public String sortKey() {
            return sortKey;
        }
    }

    public static final class Item {
        private final Key key;
        private final Map<String, String> attributes;

        public Item(Key key, Map<String, String> attributes) {
            this.key = Objects.requireNonNull(key, "key");
            this.attributes = new HashMap<>(attributes);
        }

        public Key key() {
            return key;
        }

        public Map<String, String> attributes() {
            return new HashMap<>(attributes);
        }
    }

    public Key messageKey(String chatId, long messageOrdinal) {
        return new Key("CHAT#" + chatId, String.format("MSG#%020d", messageOrdinal));
    }

    public Key userPreferenceKey(String userId) {
        return new Key("USER#" + userId, null);
    }

    public Item buildItem(Key key, Map<String, String> attributes) {
        return new Item(key, attributes);
    }
}
