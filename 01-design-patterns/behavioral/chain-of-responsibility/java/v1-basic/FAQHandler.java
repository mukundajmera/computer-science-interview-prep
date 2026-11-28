package chainofresponsibility.v1;

/**
 * Automated FAQ handler that resolves severity-1 tickets.
 *
 * <p>Time Complexity: O(1) per check and processing step.
 * Space Complexity: O(1).
 */
public class FAQHandler extends SupportHandler {

    private static final int HANDLED_SEVERITY = 1;

    /**
     * Creates an FAQ handler with no successor.
     */
    public FAQHandler() {
        super();
    }

    /**
     * Creates an FAQ handler linked to the given successor.
     *
     * @param next the next handler in the chain
     */
    public FAQHandler(SupportHandler next) {
        super(next);
    }

    @Override
    protected boolean canHandle(SupportTicket ticket) {
        return ticket.getSeverity() == HANDLED_SEVERITY;
    }

    @Override
    protected void process(SupportTicket ticket) {
        System.out.println("[FAQ Bot] Answered: " + ticket.getIssue());
    }
}
