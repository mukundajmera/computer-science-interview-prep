package chainofresponsibility.v1;

import java.util.Objects;

/**
 * Abstract base handler in the Chain of Responsibility support ticket pipeline.
 *
 * <p>Each handler either processes a ticket when {@link #canHandle(SupportTicket)}
 * returns {@code true} or delegates it to the next handler in the chain.
 *
 * <p>Time Complexity: O(n) worst case for {@link #handle(SupportTicket)}, where n
 * is the number of handlers in the chain.
 * Space Complexity: O(n) call stack depth in the worst case.
 */
public abstract class SupportHandler {

    private SupportHandler next;

    /**
     * Creates a handler with no successor configured yet.
     */
    protected SupportHandler() {
        this(null);
    }

    /**
     * Creates a handler with an optional successor injected at construction time.
     *
     * @param next the next handler in the chain, or {@code null} if this is the tail
     */
    protected SupportHandler(SupportHandler next) {
        this.next = next;
    }

    /**
     * Links the next handler in the chain and returns it for fluent composition.
     *
     * <p>Time Complexity: O(1). Space Complexity: O(1).
     *
     * @param handler the successor handler
     * @return the successor handler passed in
     */
    public SupportHandler setNext(SupportHandler handler) {
        this.next = handler;
        return handler;
    }

    /**
     * Processes the ticket if this handler qualifies; otherwise forwards it along the chain.
     *
     * <p>Time Complexity: O(n) worst case across a chain of n handlers.
     * Space Complexity: O(n) stack frames in the worst case.
     *
     * @param ticket the support ticket to handle
     */
    public void handle(SupportTicket ticket) {
        Objects.requireNonNull(ticket, "ticket must not be null");
        if (canHandle(ticket)) {
            process(ticket);
        } else if (next != null) {
            next.handle(ticket);
        } else {
            System.out.println("No handler for: " + ticket.getIssue());
        }
    }

    /**
     * Determines whether this handler is responsible for the given ticket.
     *
     * @param ticket the ticket to inspect
     * @return {@code true} if this handler should process the ticket
     */
    protected abstract boolean canHandle(SupportTicket ticket);

    /**
     * Executes handling logic for a matching ticket.
     *
     * @param ticket the ticket to process
     */
    protected abstract void process(SupportTicket ticket);
}
