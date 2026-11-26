from locker import Locker
from package_size import PackageSize


if __name__ == "__main__":
    locker = Locker(1, 1, 1)
    token = locker.deposit_package(PackageSize.SMALL)

    print(f"Issued token: {token}")
    print(f"Pickup success: {locker.pickup(token) if token else False}")
