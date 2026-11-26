package v1simple;

public class Demo {
    public static void main(String[] args) throws InterruptedException {
        DistributedLock.LockServer server = new DistributedLock.LockServer();

        System.out.println("Client 1 trying to acquire lock...");
        DistributedLock lock1 = new DistributedLock(server, "my-resource", 5000, 2000);
        Long token1 = lock1.acquire(true, null);
        System.out.println("Client 1 acquired lock with token: " + token1);

        System.out.println("Client 2 trying to acquire lock (non-blocking)...");
        DistributedLock lock2 = new DistributedLock(server, "my-resource", 5000, 2000);
        Long token2 = lock2.acquire(false, null);
        System.out.println("Client 2 acquired lock: " + (token2 != null));

        System.out.println("Client 1 releasing lock...");
        lock1.release();

        System.out.println("Client 2 trying to acquire lock again...");
        token2 = lock2.acquire(true, null);
        System.out.println("Client 2 acquired lock with token: " + token2);

        lock2.release();
    }
}
