package v1_simple;

import java.util.Arrays;

public class Demo {
    public static void main(String[] args) {
        System.out.println("Read Scaling Demo");
        ReadReplicaRouter router = new ReadReplicaRouter("db-primary", Arrays.asList("db-replica-1", "db-replica-2"), 5000);

        System.out.println("Write to primary: " + router.routeWrite("user1"));
        System.out.println("Read without write: " + router.routeRead("user2"));

        router.updateReplicaLag("db-replica-1", 100);
        router.updateReplicaHealth("db-replica-2", false);

        System.out.println("Read eligible replica: " + router.routeRead("user3"));
    }
}
