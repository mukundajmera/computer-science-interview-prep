package mediator.v1;

/**
 * Concrete colleague that sends and receives chat room messages via a {@link ChatMediator}.
 *
 * <p>Time Complexity: O(n) for {@link #send(String)} via mediator broadcast;
 * O(1) for {@link #receive(String, String)}.
 * Space Complexity: O(1).
 */
public class ChatUser extends User {

    /**
     * Creates a chat user associated with the given mediator.
     *
     * @param mediator the mediator coordinating message delivery
     * @param name     display name of the user
     */
    public ChatUser(ChatMediator mediator, String name) {
        super(mediator, name);
    }

    @Override
    public void send(String message) {
        System.out.println(name + " sends: " + message);
        mediator.sendMessage(message, this);
    }

    @Override
    public void receive(String message, String from) {
        System.out.println(name + " received from " + from + ": " + message);
    }
}
