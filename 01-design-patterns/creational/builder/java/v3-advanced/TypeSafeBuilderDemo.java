package builder.v3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * v3-advanced: Type-Safe Staged Builder with Runtime Invariant Validation.
 * Uses compile-time interface chaining (Stages) to force mandatory fields
 * (SELECT -> FROM) before optional clauses (WHERE, LIMIT) and terminal validation.
 */
public class TypeSafeBuilderDemo {

    public static final class SqlQuery {
        private final List<String> columns;
        private final String table;
        private final String whereClause;
        private final Integer limit;

        private SqlQuery(List<String> columns, String table, String whereClause, Integer limit) {
            this.columns = Collections.unmodifiableList(new ArrayList<>(columns));
            this.table = table;
            this.whereClause = whereClause;
            this.limit = limit;
        }

        public List<String> getColumns() {
            return columns;
        }

        public String getTable() {
            return table;
        }

        public String getWhereClause() {
            return whereClause;
        }

        public Integer getLimit() {
            return limit;
        }

        public String toSql() {
            StringBuilder sb = new StringBuilder();
            sb.append("SELECT ").append(String.join(", ", columns));
            sb.append(" FROM ").append(table);
            if (whereClause != null && !whereClause.trim().isEmpty()) {
                sb.append(" WHERE ").append(whereClause.trim());
            }
            if (limit != null) {
                sb.append(" LIMIT ").append(limit);
            }
            return sb.toString();
        }

        // --- Staged Builder Interfaces ---

        public interface SelectStage {
            FromStage select(String... columns);
        }

        public interface FromStage {
            WhereStage from(String table);
        }

        public interface WhereStage extends BuilderStage {
            LimitStage where(String condition);
        }

        public interface LimitStage extends BuilderStage {
            BuilderStage limit(int limit);
        }

        public interface BuilderStage {
            SqlQuery build();
        }

        public static SelectStage builder() {
            return new StagedBuilder();
        }

        private static class StagedBuilder implements SelectStage, FromStage, WhereStage, LimitStage {
            private final List<String> columns = new ArrayList<>();
            private String table;
            private String whereClause;
            private Integer limit;

            @Override
            public FromStage select(String... cols) {
                if (cols == null || cols.length == 0) {
                    throw new IllegalArgumentException("At least one column must be specified");
                }
                for (String col : cols) {
                    if (col == null || col.trim().isEmpty()) {
                        throw new IllegalArgumentException("Column name cannot be blank");
                    }
                    this.columns.add(col.trim());
                }
                return this;
            }

            @Override
            public WhereStage from(String table) {
                if (table == null || table.trim().isEmpty()) {
                    throw new IllegalArgumentException("Table name cannot be blank");
                }
                this.table = table.trim();
                return this;
            }

            @Override
            public LimitStage where(String condition) {
                if (condition != null && !condition.trim().isEmpty()) {
                    this.whereClause = condition.trim();
                }
                return this;
            }

            @Override
            public BuilderStage limit(int limitValue) {
                if (limitValue <= 0) {
                    throw new IllegalArgumentException("Limit must be positive: " + limitValue);
                }
                this.limit = limitValue;
                return this;
            }

            @Override
            public SqlQuery build() {
                if (columns.isEmpty()) {
                    throw new IllegalStateException("Cannot build query without selected columns");
                }
                if (table == null || table.trim().isEmpty()) {
                    throw new IllegalStateException("Cannot build query without target table");
                }
                return new SqlQuery(columns, table, whereClause, limit);
            }
        }
    }

    public static void main(String[] args) {
        SqlQuery query = SqlQuery.builder()
                .select("id", "username", "email")
                .from("users")
                .where("active = 1")
                .limit(50)
                .build();

        System.out.println("Generated SQL: " + query.toSql());
    }
}
