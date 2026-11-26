from fallback_size_policy import FallbackSizePolicy
from locker import Locker
from package_size import PackageSize


if __name__ == "__main__":
    locker = Locker(1, 0, 1)
    locker.set_allocation_policy(FallbackSizePolicy())

    token = locker.deposit_package(PackageSize.SMALL)
    print(f"Issued token with fallback policy: {token}")
