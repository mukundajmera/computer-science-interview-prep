package chainofresponsibility.v1;

import java.util.Objects;

/**
 * Immutable support ticket carrying an issue description and severity level.
 *
 * <p>Time Complexity: O(1) for construction and field access.
 * Space Complexity: O(1).
 */
public class SupportTicket {

    private final String issue;
    private final int severity;

    /**
     * Creates a support ticket with the given issue summary and severity level.
     *
     * @param issue    short description of the reported problem
     * @param severity numeric severity level (1 = FAQ, 2 = L1, 3 = L2, 4+ = Manager)
     */
    public SupportTicket(String issue, int severity) {
        this.issue = Objects.requireNonNull(issue, "issue must not be null");
        this.severity = severity;
    }

    /**
     * Returns the issue description.
     *
     * @return the ticket issue text
     */
    public String getIssue() {
        return issue;
    }

    /**
     * Returns the numeric severity level.
     *
     * @return the ticket severity
     */
    public int getSeverity() {
        return severity;
    }
}
