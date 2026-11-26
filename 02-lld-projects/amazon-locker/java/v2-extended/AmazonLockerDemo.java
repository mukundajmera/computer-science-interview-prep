public class AmazonLockerDemo {
    public static void main(String[] args) {
        Locker locker = new Locker(1, 0, 1);
        locker.setAllocationPolicy(new FallbackSizePolicy());

        String token = locker.depositPackage(PackageSize.SMALL);
        System.out.println("Issued token with fallback policy: " + token);
    }
}
