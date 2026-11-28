package mediator.v1;

/**
 * Mediator interface that coordinates message exchange between chat users.
 *
 * <p>Time Complexity: Implementation-dependent (O(n) broadcast in {@link ChatRoom}).
 * Space Complexity: O(1) for the contract.
 */
public interface ChatMediator {

    /**
     * Delivers a message from the sender to all other registered participants.
     *
     * @param message the message text to broadcast
     * @param sender  the user sending the message
     */
    void sendMessage(String message, User sender);

    /**
     * Registers a user with the mediator so they can send and receive messages.
     *
     * @param user the participant to register
     */
    void addUser(User user);
}
