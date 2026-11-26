public class AmazonLockerDemo {
    public static void main(String[] args) {
        Locker locker = new Locker(1, 1, 1);
        String reservationId = locker.reserveCompartment(PackageSize.SMALL);
        String token = locker.confirmDeposit(reservationId);

        System.out.println("Reservation: " + reservationId);
        System.out.println("Token: " + token);
    }
}
