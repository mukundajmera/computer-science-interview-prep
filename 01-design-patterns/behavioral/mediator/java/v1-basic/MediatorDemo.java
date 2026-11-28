package mediator.v1;

/**
 * Mediator Pattern - V1 Basic: Chat Room.
 *
 * <p>Demonstrates decoupling chat participants by routing all messages through a
 * central {@link ChatRoom} mediator.
 *
 * <p>Time Complexity: O(n) per broadcast message for n registered users.
 * Space Complexity: O(n) for storing participants in the chat room.
 */
public class MediatorDemo {

    /**
     * Creates a chat room, registers three users, and exchanges sample messages.
     *
     * @param args unused command-line arguments
     */
    public static void main(String[] args) {
        ChatRoom chatRoom = new ChatRoom();

        ChatUser alice = new ChatUser(chatRoom, "Alice");
        ChatUser bob = new ChatUser(chatRoom, "Bob");
        ChatUser charlie = new ChatUser(chatRoom, "Charlie");

        chatRoom.addUser(alice);
        chatRoom.addUser(bob);
        chatRoom.addUser(charlie);

        System.out.println("\n=== Chat ===");
        alice.send("Hello everyone!");
        System.out.println();
        bob.send("Hi Alice!");
    }
}
