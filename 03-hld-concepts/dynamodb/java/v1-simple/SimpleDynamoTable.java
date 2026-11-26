import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Interview-scale DynamoDB table model with PK/SK and a lightweight GSI.
 */
public class SimpleDynamoTable {
    public static final class Item {
        public final String partitionKey;
        public final String sortKey;
        public final Map<String, Object> attributes;

        public Item(String partitionKey, String sortKey, Map<String, Object> attributes) {
            this.partitionKey = partitionKey;
            this.sortKey = sortKey;
            this.attributes = attributes;
        }
    }

    public static final class GsiDefinition {
        public final String name;
        public final String partitionAttr;
        public final String sortAttr;

        public GsiDefinition(String name, String partitionAttr, String sortAttr) {
            this.name = name;
            this.partitionAttr = partitionAttr;
            this.sortAttr = sortAttr;
        }
    }

    private final Map<String, Map<String, Item>> table = new HashMap<>();
    private final Map<String, GsiDefinition> indexes = new HashMap<>();

    public void defineGsi(String name, String partitionAttr, String sortAttr) {
        indexes.put(name, new GsiDefinition(name, partitionAttr, sortAttr));
    }

    public void putItem(String partitionKey, String sortKey, Map<String, Object> attributes) {
        table.computeIfAbsent(partitionKey, ignored -> new HashMap<>())
            .put(sortKey, new Item(partitionKey, sortKey, new HashMap<>(attributes)));
    }

    public Item getItem(String partitionKey, String sortKey) {
        Map<String, Item> partition = table.get(partitionKey);
        if (partition == null) {
            return null;
        }
        return partition.get(sortKey);
    }

    public boolean deleteItem(String partitionKey, String sortKey) {
        Map<String, Item> partition = table.get(partitionKey);
        if (partition == null) {
            return false;
        }
        return partition.remove(sortKey) != null;
    }

    public List<Item> query(String partitionKey) {
        return sortBySortKey(new ArrayList<>(table.getOrDefault(partitionKey, Collections.emptyMap()).values()));
    }

    public List<Item> queryRange(String partitionKey, String fromSortKey, String toSortKey) {
        List<Item> items = new ArrayList<>();
        for (Item item : query(partitionKey)) {
            if (item.sortKey.compareTo(fromSortKey) >= 0 && item.sortKey.compareTo(toSortKey) <= 0) {
                items.add(item);
            }
        }
        return items;
    }

    public List<Item> queryGsi(String indexName, String partitionValue) {
        GsiDefinition definition = indexes.get(indexName);
        if (definition == null) {
            return new ArrayList<>();
        }
        List<Item> results = new ArrayList<>();
        for (Map<String, Item> partition : table.values()) {
            for (Item item : partition.values()) {
                Object gsiPk = item.attributes.get(definition.partitionAttr);
                if (partitionValue.equals(gsiPk)) {
                    results.add(item);
                }
            }
        }
        if (definition.sortAttr != null) {
            results.sort(Comparator.comparing(item -> String.valueOf(item.attributes.getOrDefault(definition.sortAttr, ""))));
        }
        return results;
    }

    public List<Item> scan(int limit, int offset) {
        List<Item> allItems = new ArrayList<>();
        for (Map<String, Item> partition : table.values()) {
            allItems.addAll(partition.values());
        }
        allItems = sortBySortKey(allItems);
        int start = Math.min(offset, allItems.size());
        int end = Math.min(start + limit, allItems.size());
        return new ArrayList<>(allItems.subList(start, end));
    }

    private List<Item> sortBySortKey(List<Item> items) {
        items.sort(Comparator.comparing(item -> item.sortKey));
        return items;
    }
}
