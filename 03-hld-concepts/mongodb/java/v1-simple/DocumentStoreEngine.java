import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.stream.Collectors;

public class DocumentStoreEngine {

    public static class Document extends HashMap<String, Object> {
        public Document() {
            super();
        }
        public Document(Map<String, Object> map) {
            super(map);
        }
        public Document append(String key, Object value) {
            this.put(key, value);
            return this;
        }
    }

    public static class Collection {
        private final Map<String, Document> documents = new ConcurrentHashMap<>();
        private final ReadWriteLock lock = new ReentrantReadWriteLock();
        private final Map<String, Map<Object, Set<String>>> indexes = new ConcurrentHashMap<>();
        private final AtomicInteger idGenerator = new AtomicInteger(1);

        public String insert(Document doc) {
            lock.writeLock().lock();
            try {
                String id = doc.containsKey("_id") ? doc.get("_id").toString() : String.valueOf(idGenerator.getAndIncrement());
                doc.put("_id", id);
                documents.put(id, new Document(doc)); // Clone to store

                // Update indexes
                for (String indexedField : indexes.keySet()) {
                    Object val = getFieldValue(doc, indexedField);
                    if (val != null) {
                        indexes.get(indexedField).computeIfAbsent(val, k -> new HashSet<>()).add(id);
                    }
                }
                return id;
            } finally {
                lock.writeLock().unlock();
            }
        }

        public void createIndex(String field) {
            lock.writeLock().lock();
            try {
                if (!indexes.containsKey(field)) {
                    Map<Object, Set<String>> index = new HashMap<>();
                    for (Map.Entry<String, Document> entry : documents.entrySet()) {
                        Object val = getFieldValue(entry.getValue(), field);
                        if (val != null) {
                            index.computeIfAbsent(val, k -> new HashSet<>()).add(entry.getKey());
                        }
                    }
                    indexes.put(field, index);
                }
            } finally {
                lock.writeLock().unlock();
            }
        }

        public List<Document> find(Document query, Document projection) {
            lock.readLock().lock();
            try {
                Set<String> candidateIds = null;

                if (query != null && !query.isEmpty()) {
                    for (Map.Entry<String, Object> entry : query.entrySet()) {
                        String field = entry.getKey();
                        Object condition = entry.getValue();

                        if (indexes.containsKey(field)) {
                            if (condition instanceof Map) {
                                Map<String, Object> operatorMap = (Map<String, Object>) condition;
                                if (operatorMap.containsKey("$eq")) {
                                    Set<String> indexedIds = indexes.get(field).get(operatorMap.get("$eq"));
                                    candidateIds = intersect(candidateIds, indexedIds);
                                }
                            } else {
                                Set<String> indexedIds = indexes.get(field).get(condition);
                                candidateIds = intersect(candidateIds, indexedIds);
                            }
                        }
                    }
                }

                java.util.Collection<Document> docsToSearch;
                if (candidateIds != null) {
                    docsToSearch = candidateIds.stream()
                        .map(documents::get)
                        .filter(Objects::nonNull)
                        .collect(Collectors.toList());
                } else {
                    docsToSearch = documents.values();
                }

                List<Document> results = new ArrayList<>();
                for (Document doc : docsToSearch) {
                    if (matches(doc, query)) {
                        results.add(project(doc, projection));
                    }
                }
                return results;
            } finally {
                lock.readLock().unlock();
            }
        }

        private Set<String> intersect(Set<String> current, Set<String> newSet) {
            if (newSet == null) return new HashSet<>();
            if (current == null) return new HashSet<>(newSet);
            current.retainAll(newSet);
            return current;
        }

        private boolean matches(Document doc, Document query) {
            if (query == null || query.isEmpty()) return true;

            for (Map.Entry<String, Object> entry : query.entrySet()) {
                String field = entry.getKey();
                Object condition = entry.getValue();

                Object docValue = getFieldValue(doc, field);

                if (condition instanceof Map) {
                    Map<String, Object> operatorMap = (Map<String, Object>) condition;
                    for (Map.Entry<String, Object> opEntry : operatorMap.entrySet()) {
                        String op = opEntry.getKey();
                        Object opVal = opEntry.getValue();

                        switch (op) {
                            case "$eq":
                                if (!Objects.equals(docValue, opVal)) return false;
                                break;
                            case "$gt":
                                if (docValue instanceof Comparable && opVal instanceof Comparable) {
                                    if (((Comparable) docValue).compareTo(opVal) <= 0) return false;
                                } else {
                                    return false;
                                }
                                break;
                            case "$in":
                                if (opVal instanceof java.util.Collection) {
                                    if (!((java.util.Collection<?>) opVal).contains(docValue)) return false;
                                } else {
                                    return false;
                                }
                                break;
                            case "$elemMatch":
                                if (docValue instanceof List) {
                                    boolean matchedElem = false;
                                    for (Object elem : (List<?>) docValue) {
                                        if (elem instanceof Map) {
                                            if (matches(new Document((Map<String, Object>) elem), new Document((Map<String, Object>) opVal))) {
                                                matchedElem = true;
                                                break;
                                            }
                                        }
                                    }
                                    if (!matchedElem) return false;
                                } else {
                                    return false;
                                }
                                break;
                            default:
                                return false; // Unsupported operator
                        }
                    }
                } else {
                    if (!Objects.equals(docValue, condition)) return false;
                }
            }
            return true;
        }

        private Document project(Document doc, Document projection) {
            if (projection == null || projection.isEmpty()) {
                return new Document(doc);
            }
            Document projected = new Document();
            boolean includeMode = projection.values().stream().anyMatch(v -> Objects.equals(v, 1));

            if (includeMode) {
                // Always include _id unless explicitly excluded
                if (!projection.containsKey("_id") || Objects.equals(projection.get("_id"), 1)) {
                    projected.put("_id", doc.get("_id"));
                }
                for (String key : projection.keySet()) {
                    if (Objects.equals(projection.get(key), 1)) {
                        Object val = getFieldValue(doc, key);
                        if (val != null) {
                            setFieldValue(projected, key, val);
                        }
                    }
                }
            } else {
                projected.putAll(doc);
                for (String key : projection.keySet()) {
                    if (Objects.equals(projection.get(key), 0)) {
                        removeFieldValue(projected, key);
                    }
                }
            }
            return projected;
        }

        private Object getFieldValue(Map<String, Object> doc, String fieldPath) {
            String[] parts = fieldPath.split("\\.");
            Object current = doc;
            for (String part : parts) {
                if (current instanceof Map) {
                    current = ((Map<String, Object>) current).get(part);
                } else {
                    return null;
                }
            }
            return current;
        }

        private void setFieldValue(Map<String, Object> doc, String fieldPath, Object value) {
            String[] parts = fieldPath.split("\\.");
            Map<String, Object> current = doc;
            for (int i = 0; i < parts.length - 1; i++) {
                current = (Map<String, Object>) current.computeIfAbsent(parts[i], k -> new Document());
            }
            current.put(parts[parts.length - 1], value);
        }

        private void removeFieldValue(Map<String, Object> doc, String fieldPath) {
            String[] parts = fieldPath.split("\\.");
            Map<String, Object> current = doc;
            for (int i = 0; i < parts.length - 1; i++) {
                if (current.containsKey(parts[i]) && current.get(parts[i]) instanceof Map) {
                    current = (Map<String, Object>) current.get(parts[i]);
                } else {
                    return;
                }
            }
            current.remove(parts[parts.length - 1]);
        }
    }

    private final Map<String, Collection> collections = new ConcurrentHashMap<>();

    public Collection getCollection(String name) {
        return collections.computeIfAbsent(name, k -> new Collection());
    }

    public String insert(String collectionName, Document doc) {
        return getCollection(collectionName).insert(doc);
    }

    public void createIndex(String collectionName, String field) {
        getCollection(collectionName).createIndex(field);
    }

    public List<Document> find(String collectionName, Document query) {
        return getCollection(collectionName).find(query, null);
    }

    public List<Document> find(String collectionName, Document query, Document projection) {
        return getCollection(collectionName).find(query, projection);
    }
}
