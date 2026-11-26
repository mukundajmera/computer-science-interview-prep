import java.util.*;
import java.util.function.Predicate;
import java.util.function.BiPredicate;
import java.util.stream.Collectors;

public class RelationalQueryEngine {

    public static class Column {
        public final String name;
        public final Class<?> type;
        public final boolean primaryKey;
        public final boolean unique;

        public Column(String name, Class<?> type, boolean primaryKey, boolean unique) {
            this.name = name;
            this.type = type;
            this.primaryKey = primaryKey;
            this.unique = unique;
        }
    }

    public static class Table {
        public final String name;
        public final Map<String, Column> columns;
        private final List<Map<String, Object>> rows;
        private final List<String> primaryKeys;
        private final List<String> uniqueColumns;

        public Table(String name, List<Column> cols) {
            this.name = name;
            this.columns = new HashMap<>();
            this.primaryKeys = new ArrayList<>();
            this.uniqueColumns = new ArrayList<>();
            this.rows = new ArrayList<>();

            for (Column col : cols) {
                this.columns.put(col.name, col);
                if (col.primaryKey) {
                    this.primaryKeys.add(col.name);
                }
                if (col.unique || col.primaryKey) {
                    this.uniqueColumns.add(col.name);
                }
            }
        }

        private void validateRow(Map<String, Object> row, boolean isUpdate, Map<String, Object> originalRow) {
            // Type check
            for (Map.Entry<String, Object> entry : row.entrySet()) {
                String colName = entry.getKey();
                Object value = entry.getValue();
                if (columns.containsKey(colName) && value != null) {
                    Column col = columns.get(colName);
                    if (!col.type.isInstance(value)) {
                        throw new IllegalArgumentException("Column '" + colName + "' expects " + col.type.getSimpleName() + ", got " + value.getClass().getSimpleName());
                    }
                }
            }

            // Missing primary keys
            if (!isUpdate) {
                for (String pk : primaryKeys) {
                    if (!row.containsKey(pk) || row.get(pk) == null) {
                        throw new IllegalArgumentException("Primary key '" + pk + "' cannot be null");
                    }
                }
            }

            // PK and Unique constraints
            for (String colName : uniqueColumns) {
                if (row.containsKey(colName) && row.get(colName) != null) {
                    Object val = row.get(colName);
                    for (Map<String, Object> r : rows) {
                        if (isUpdate && r == originalRow) {
                            continue;
                        }
                        if (Objects.equals(r.get(colName), val)) {
                            throw new IllegalArgumentException("Unique constraint failed for column '" + colName + "'");
                        }
                    }
                }
            }
        }

        public void insert(Map<String, Object> row) {
            Map<String, Object> fullRow = new HashMap<>();
            for (String colName : columns.keySet()) {
                fullRow.put(colName, row.get(colName));
            }
            validateRow(fullRow, false, null);
            rows.add(fullRow);
        }

        public void update(Predicate<Map<String, Object>> predicate, Map<String, Object> updates) {
            for (Map<String, Object> r : rows) {
                if (predicate.test(r)) {
                    Map<String, Object> newRow = new HashMap<>(r);
                    newRow.putAll(updates);
                    validateRow(newRow, true, r);
                    r.putAll(updates);
                }
            }
        }

        public void delete(Predicate<Map<String, Object>> predicate) {
            rows.removeIf(predicate);
        }

        public List<Map<String, Object>> select(Predicate<Map<String, Object>> predicate) {
            return rows.stream()
                    .filter(predicate != null ? predicate : r -> true)
                    .map(HashMap::new)
                    .collect(Collectors.toList());
        }

        // For testing / engine access
        public List<Map<String, Object>> getRows() {
            return rows;
        }
    }

    private final Map<String, Table> tables = new HashMap<>();

    public void createTable(Table table) {
        tables.put(table.name, table);
    }

    public void insert(String tableName, Map<String, Object> row) {
        tables.get(tableName).insert(row);
    }

    public void update(String tableName, Predicate<Map<String, Object>> predicate, Map<String, Object> updates) {
        tables.get(tableName).update(predicate, updates);
    }

    public void delete(String tableName, Predicate<Map<String, Object>> predicate) {
        tables.get(tableName).delete(predicate);
    }

    public List<Map<String, Object>> select(String tableName, Predicate<Map<String, Object>> predicate) {
        return tables.get(tableName).select(predicate);
    }

    public List<Map<String, Object>> innerJoin(String table1Name, String table2Name,
                                               BiPredicate<Map<String, Object>, Map<String, Object>> joinCondition,
                                               Predicate<Map<String, Object>> predicate) {
        Table t1 = tables.get(table1Name);
        Table t2 = tables.get(table2Name);
        List<Map<String, Object>> result = new ArrayList<>();

        for (Map<String, Object> r1 : t1.getRows()) {
            for (Map<String, Object> r2 : t2.getRows()) {
                if (joinCondition.test(r1, r2)) {
                    Map<String, Object> merged = new HashMap<>();
                    for (Map.Entry<String, Object> e : r1.entrySet()) {
                        merged.put(table1Name + "." + e.getKey(), e.getValue());
                    }
                    for (Map.Entry<String, Object> e : r2.entrySet()) {
                        merged.put(table2Name + "." + e.getKey(), e.getValue());
                    }

                    if (predicate == null || predicate.test(merged)) {
                        result.add(merged);
                    }
                }
            }
        }
        return result;
    }

    public List<Map<String, Object>> groupBy(String tableName, List<String> groupCols, String aggCol, String aggFunc) {
        Table t1 = tables.get(tableName);
        Map<List<Object>, List<Object>> groups = new HashMap<>();

        for (Map<String, Object> r : t1.getRows()) {
            List<Object> key = new ArrayList<>();
            for (String col : groupCols) {
                key.add(r.get(col));
            }
            groups.putIfAbsent(key, new ArrayList<>());
            if (r.containsKey(aggCol) && r.get(aggCol) != null) {
                groups.get(key).add(r.get(aggCol));
            }
        }

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<List<Object>, List<Object>> entry : groups.entrySet()) {
            Map<String, Object> row = new HashMap<>();
            List<Object> key = entry.getKey();
            for (int i = 0; i < groupCols.size(); i++) {
                row.put(groupCols.get(i), key.get(i));
            }

            List<Object> vals = entry.getValue();
            if ("COUNT".equalsIgnoreCase(aggFunc)) {
                row.put("COUNT(" + aggCol + ")", vals.size());
            } else if ("SUM".equalsIgnoreCase(aggFunc)) {
                double sum = 0.0;
                for (Object v : vals) {
                    if (v instanceof Number) {
                        sum += ((Number) v).doubleValue();
                    }
                }
                row.put("SUM(" + aggCol + ")", sum);
            } else {
                throw new IllegalArgumentException("Unknown aggregation function " + aggFunc);
            }
            result.add(row);
        }
        return result;
    }
}
