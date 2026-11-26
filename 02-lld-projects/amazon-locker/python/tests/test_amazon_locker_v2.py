import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))
for module_name in [
    "locker",
    "package_size",
    "access_token",
    "compartment",
    "compartment_status",
    "exact_size_policy",
    "fallback_size_policy",
    "allocation_policy",
]:
    sys.modules.pop(module_name, None)

from fallback_size_policy import FallbackSizePolicy
from locker import Locker
from package_size import PackageSize


class MutableClock:
    def __init__(self, now: datetime):
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


class AmazonLockerV2Test(unittest.TestCase):
    def test_fallback_policy_allocates_larger_compartment(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(0, 0, 1, clock=clock.now)

        self.assertIsNone(locker.deposit_package(PackageSize.SMALL))
        locker.set_allocation_policy(FallbackSizePolicy())

        token = locker.deposit_package(PackageSize.SMALL)
        self.assertIsNotNone(token)
        self.assertTrue(locker.pickup(token))

    def test_out_of_service_compartment_is_not_allocated(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(1, 0, 0, clock=clock.now)

        self.assertTrue(locker.mark_compartment_out_of_service("S-1"))
        self.assertIsNone(locker.deposit_package(PackageSize.SMALL))


if __name__ == '__main__':
    unittest.main()
