import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class PostgresReadWritePlannerTest {

    @Test
    public void testWriteOperationRoutesToPrimary() {
        PostgresReadWritePlanner planner = new PostgresReadWritePlanner();
        PostgresReadWritePlanner.QueryContext context = new PostgresReadWritePlanner.QueryContext(
                PostgresReadWritePlanner.OperationType.WRITE, false, 1000L);
        PostgresReadWritePlanner.Route route = planner.decideRoute(context, 100L);
        assertEquals(PostgresReadWritePlanner.Route.PRIMARY, route);
    }

    @Test
    public void testReadWithReadAfterWriteRoutesToPrimary() {
        PostgresReadWritePlanner planner = new PostgresReadWritePlanner();
        PostgresReadWritePlanner.QueryContext context = new PostgresReadWritePlanner.QueryContext(
                PostgresReadWritePlanner.OperationType.READ, true, 1000L);
        PostgresReadWritePlanner.Route route = planner.decideRoute(context, 100L);
        assertEquals(PostgresReadWritePlanner.Route.PRIMARY, route);
    }

    @Test
    public void testReadWithHighLagRoutesToPrimary() {
        PostgresReadWritePlanner planner = new PostgresReadWritePlanner();
        PostgresReadWritePlanner.QueryContext context = new PostgresReadWritePlanner.QueryContext(
                PostgresReadWritePlanner.OperationType.READ, false, 100L);
        PostgresReadWritePlanner.Route route = planner.decideRoute(context, 200L);
        assertEquals(PostgresReadWritePlanner.Route.PRIMARY, route);
    }

    @Test
    public void testReadWithLowLagRoutesToReplica() {
        PostgresReadWritePlanner planner = new PostgresReadWritePlanner();
        PostgresReadWritePlanner.QueryContext context = new PostgresReadWritePlanner.QueryContext(
                PostgresReadWritePlanner.OperationType.READ, false, 500L);
        PostgresReadWritePlanner.Route route = planner.decideRoute(context, 100L);
        assertEquals(PostgresReadWritePlanner.Route.REPLICA, route);
    }
}
