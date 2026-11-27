package chainofresponsibility.v1;

/**
 * Tier-2 support handler that investigates severity-3 tickets.
 *
 * <p>Time Complexity: O(1) per check and processing step.
 * Space Complexity: O(1).
 */
public class Level2Support extends SupportHandler {

    private static final int HANDLED_SEVERITY = 3;

    /**
     * Creates a Level 2 support handler with no successor.
     */
    public Level2Support() {
        super();
    }

    /**
     * Creates a Level 2 support handler linked to the given successor.
     *
     * @param next the next handler in the chain
     */
    public Level2Support(SupportHandler next) {
        super(next);
    }

    @Override
    protected boolean canHandle(SupportTicket ticket) {
        return ticket.getSeverity() == HANDLED_SEVERITY;
    }

    @Override
    protected void process(SupportTicket ticket) {
        System.out.println("[L2 Support] Investigating: " + ticket.getIssue());
    }
}
