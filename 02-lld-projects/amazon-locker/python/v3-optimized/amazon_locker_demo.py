from locker import Locker
from package_size import PackageSize


if __name__ == "__main__":
    locker = Locker(1, 1, 1)
    reservation_id = locker.reserve_compartment(PackageSize.SMALL)
    token = locker.confirm_deposit(reservation_id) if reservation_id else None

    print(f"Reservation: {reservation_id}")
    print(f"Token: {token}")
