package chainofresponsibility.v1;

/**
 * Tier-1 support handler that resolves severity-2 tickets.
 *
 * <p>Time Complexity: O(1) per check and processing step.
 * Space Complexity: O(1).
 */
public class Level1Support extends SupportHandler {

    private static final int HANDLED_SEVERITY = 2;

    /**
     * Creates a Level 1 support handler with no successor.
     */
    public Level1Support() {
        super();
    }

    /**
     * Creates a Level 1 support handler linked to the given successor.
     *
     * @param next the next handler in the chain
     */
    public Level1Support(SupportHandler next) {
        super(next);
    }

    @Override
    protected boolean canHandle(SupportTicket ticket) {
        return ticket.getSeverity() == HANDLED_SEVERITY;
    }

    @Override
    protected void process(SupportTicket ticket) {
        System.out.println("[L1 Support] Resolved: " + ticket.getIssue());
    }
}
