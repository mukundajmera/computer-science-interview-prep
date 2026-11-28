package mediator.v1;

import java.util.Objects;

/**
 * Abstract colleague participating in a mediated chat room.
 *
 * <p>Each user holds a reference to the {@link ChatMediator} injected via the
 * constructor rather than holding direct references to other users.
 *
 * <p>Time Complexity: O(1) for construction and name lookup.
 * Space Complexity: O(1).
 */
public abstract class User {

    protected final ChatMediator mediator;
    protected final String name;

    /**
     * Creates a user bound to the given chat mediator.
     *
     * @param mediator the mediator coordinating communication
     * @param name     display name of the user
     */
    public User(ChatMediator mediator, String name) {
        this.mediator = Objects.requireNonNull(mediator, "mediator must not be null");
        this.name = Objects.requireNonNull(name, "name must not be null");
    }

    /**
     * Returns the user's display name.
     *
     * @return the user name
     */
    public String getName() {
        return name;
    }

    /**
     * Sends a message through the mediator.
     *
     * @param message the text to send
     */
    public abstract void send(String message);

    /**
     * Handles an incoming message relayed by the mediator.
     *
     * @param message the received message text
     * @param from    the display name of the sender
     */
    public abstract void receive(String message, String from);
}
