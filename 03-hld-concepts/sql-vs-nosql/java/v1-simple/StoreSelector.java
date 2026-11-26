/** Simple SQL vs NoSQL selector based on workload requirements. */
public class StoreSelector {
    public static final class Workload {
        private final boolean needsStrongTransactions;
        private final boolean needsFlexibleSchema;
        private final boolean needsJoinHeavyQueries;
        private final boolean needsMassiveHorizontalScale;

        public Workload(boolean needsStrongTransactions,
                        boolean needsFlexibleSchema,
                        boolean needsJoinHeavyQueries,
                        boolean needsMassiveHorizontalScale) {
            this.needsStrongTransactions = needsStrongTransactions;
            this.needsFlexibleSchema = needsFlexibleSchema;
            this.needsJoinHeavyQueries = needsJoinHeavyQueries;
            this.needsMassiveHorizontalScale = needsMassiveHorizontalScale;
        }

        public boolean needsStrongTransactions() { return needsStrongTransactions; }
        public boolean needsFlexibleSchema() { return needsFlexibleSchema; }
        public boolean needsJoinHeavyQueries() { return needsJoinHeavyQueries; }
        public boolean needsMassiveHorizontalScale() { return needsMassiveHorizontalScale; }
    }

    public String chooseStore(Workload workload) {
        if (workload == null) {
            throw new IllegalArgumentException("workload must not be null");
        }
        if (workload.needsStrongTransactions() || workload.needsJoinHeavyQueries()) {
            return "SQL";
        }
        if (workload.needsMassiveHorizontalScale() || workload.needsFlexibleSchema()) {
            return "NoSQL";
        }
        return "SQL";
    }
}
