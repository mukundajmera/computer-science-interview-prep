import java.util.Objects;

/**
 * Minimal read/write routing policy for PostgreSQL-style primary + replicas.
 */
public class PostgresReadWritePlanner {

    public enum OperationType {
        READ,
        WRITE
    }

    public enum Route {
        PRIMARY,
        REPLICA
    }

    public static final class QueryContext {
        private final OperationType operationType;
        private final boolean requiresReadAfterWrite;
        private final long maxReplicaLagMs;

        public QueryContext(OperationType operationType, boolean requiresReadAfterWrite, long maxReplicaLagMs) {
            this.operationType = Objects.requireNonNull(operationType, "operationType");
            this.requiresReadAfterWrite = requiresReadAfterWrite;
            this.maxReplicaLagMs = maxReplicaLagMs;
        }

        public OperationType operationType() {
            return operationType;
        }

        public boolean requiresReadAfterWrite() {
            return requiresReadAfterWrite;
        }

        public long maxReplicaLagMs() {
            return maxReplicaLagMs;
        }
    }

    public Route decideRoute(QueryContext context, long observedReplicaLagMs) {
        if (context.operationType() == OperationType.WRITE) {
            return Route.PRIMARY;
        }
        if (context.requiresReadAfterWrite()) {
            return Route.PRIMARY;
        }
        if (observedReplicaLagMs > context.maxReplicaLagMs()) {
            return Route.PRIMARY;
        }
        return Route.REPLICA;
    }
}
