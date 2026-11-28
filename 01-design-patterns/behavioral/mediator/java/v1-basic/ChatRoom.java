package mediator.v1;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * Concrete mediator representing a chat room that broadcasts messages to all
 * participants except the sender.
 *
 * <p>Time Complexity: O(1) amortized for {@link #addUser(User)}; O(n) for
 * {@link #sendMessage(String, User)} across n registered users.
 * Space Complexity: O(n) to store registered users.
 */
public class ChatRoom implements ChatMediator {

    private final List<User> users;

    /**
     * Creates an empty chat room.
     */
    public ChatRoom() {
        this.users = new ArrayList<>();
    }

    @Override
    public void addUser(User user) {
        Objects.requireNonNull(user, "user must not be null");
        users.add(user);
        System.out.println(user.getName() + " joined the chat");
    }

    @Override
    public void sendMessage(String message, User sender) {
        Objects.requireNonNull(message, "message must not be null");
        Objects.requireNonNull(sender, "sender must not be null");
        for (User user : users) {
            if (user != sender) {
                user.receive(message, sender.getName());
            }
        }
    }
}
