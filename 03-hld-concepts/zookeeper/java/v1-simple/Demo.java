package v1_simple;

public class Demo {
    public static void main(String[] args) {
        ZkLeaderElector.ZkSimulator zk = new ZkLeaderElector.ZkSimulator();

        System.out.println("Starting ZooKeeper Leader Election Demo");

        ZkLeaderElector node1 = new ZkLeaderElector(zk, "/election", "session_1");
        node1.setOnLeadershipChange(isLeader -> {
            if (isLeader) {
                System.out.println("Node 1 became leader!");
            }
        });

        ZkLeaderElector node2 = new ZkLeaderElector(zk, "/election", "session_2");
        node2.setOnLeadershipChange(isLeader -> {
            if (isLeader) {
                System.out.println("Node 2 became leader!");
            }
        });

        ZkLeaderElector node3 = new ZkLeaderElector(zk, "/election", "session_3");
        node3.setOnLeadershipChange(isLeader -> {
            if (isLeader) {
                System.out.println("Node 3 became leader!");
            }
        });

        System.out.println("Node 1 joining election...");
        node1.joinElection();

        System.out.println("Node 2 joining election...");
        node2.joinElection();

        System.out.println("Node 3 joining election...");
        node3.joinElection();

        System.out.println("Simulating Node 1 session expiration...");
        zk.expireSession("session_1");

        System.out.println("Simulating Node 2 session expiration...");
        zk.expireSession("session_2");

        System.out.println("Demo complete.");
    }
}
