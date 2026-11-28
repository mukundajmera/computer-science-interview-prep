package chainofresponsibility.v1;

/**
 * Management escalation handler for high-severity tickets (severity 4 and above).
 *
 * <p>Time Complexity: O(1) per check and processing step.
 * Space Complexity: O(1).
 */
public class ManagerSupport extends SupportHandler {

    private static final int MIN_SEVERITY = 4;

    /**
     * Creates a manager escalation handler with no successor.
     */
    public ManagerSupport() {
        super();
    }

    /**
     * Creates a manager escalation handler linked to the given successor.
     *
     * @param next the next handler in the chain
     */
    public ManagerSupport(SupportHandler next) {
        super(next);
    }

    @Override
    protected boolean canHandle(SupportTicket ticket) {
        return ticket.getSeverity() >= MIN_SEVERITY;
    }

    @Override
    protected void process(SupportTicket ticket) {
        System.out.println("[Manager] Escalated: " + ticket.getIssue());
    }
}
