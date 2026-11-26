public class AmazonLockerDemo {
    public static void main(String[] args) {
        Locker locker = new Locker(1, 1, 1);
        String token = locker.depositPackage(PackageSize.SMALL);

        System.out.println("Issued token: " + token);
        System.out.println("Pickup success: " + locker.pickup(token));
    }
}
