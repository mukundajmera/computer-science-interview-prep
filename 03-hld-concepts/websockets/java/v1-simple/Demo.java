public class Demo {
    public static void main(String[] args) {
        ConnectionManager manager = new ConnectionManager();
        manager.connect("chat-1", "u1");
        manager.connect("chat-1", "u2");
        System.out.println(manager.broadcastTargets("chat-1"));
    }
}
