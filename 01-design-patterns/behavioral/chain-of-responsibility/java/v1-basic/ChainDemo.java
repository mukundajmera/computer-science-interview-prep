package chainofresponsibility.v1;

/**
 * Chain of Responsibility Pattern - V1 Basic: Support Ticket Handling.
 *
 * <p>Demonstrates passing support tickets along an escalation chain from FAQ bot
 * through Level 1, Level 2, and Manager handlers.
 *
 * <p>Time Complexity: O(n) per ticket for a chain of n handlers.
 * Space Complexity: O(n) for the chain links and call stack depth.
 */
public class ChainDemo {

    /**
     * Builds the support escalation chain and dispatches sample tickets.
     *
     * @param args unused command-line arguments
     */
    public static void main(String[] args) {
        SupportHandler faq = new FAQHandler();
        faq.setNext(new Level1Support())
                .setNext(new Level2Support())
                .setNext(new ManagerSupport());

        System.out.println("=== Support Tickets ===");
        faq.handle(new SupportTicket("Password reset", 1));
        faq.handle(new SupportTicket("Login issue", 2));
        faq.handle(new SupportTicket("System bug", 3));
        faq.handle(new SupportTicket("Data breach", 5));
    }
}
