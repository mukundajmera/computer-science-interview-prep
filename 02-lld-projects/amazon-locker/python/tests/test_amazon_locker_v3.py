import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))
for module_name in [
    "locker",
    "package_size",
    "access_token",
    "compartment",
    "compartment_status",
    "reservation",
    "reservation_status",
    "allocation_policy",
    "fallback_size_policy",
    "exact_size_policy",
    "clock",
]:
    sys.modules.pop(module_name, None)

from compartment_status import CompartmentStatus
from locker import Locker
from package_size import PackageSize


class MutableClock:
    def __init__(self, now: datetime):
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


class AmazonLockerV3Test(unittest.TestCase):
    def test_reservation_confirm_and_pickup(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(1, 0, 0, clock=clock)

        reservation_id = locker.reserve_compartment(PackageSize.SMALL)
        self.assertEqual("R-1", reservation_id)
        self.assertEqual(CompartmentStatus.OCCUPIED, locker.get_compartment_status("S-1"))

        token = locker.confirm_deposit(reservation_id)
        self.assertEqual("T-1", token)
        self.assertTrue(locker.pickup(token))
        self.assertEqual(CompartmentStatus.AVAILABLE, locker.get_compartment_status("S-1"))

    def test_cancel_and_expire_reservation(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(1, 0, 0, clock=clock, reservation_ttl=timedelta(minutes=1))

        reservation_id = locker.reserve_compartment(PackageSize.SMALL)
        self.assertTrue(locker.cancel_reservation(reservation_id))
        self.assertEqual(CompartmentStatus.AVAILABLE, locker.get_compartment_status("S-1"))

        reservation_id = locker.reserve_compartment(PackageSize.SMALL)
        clock.advance(timedelta(minutes=2))
        self.assertIsNone(locker.confirm_deposit(reservation_id))
        self.assertEqual(CompartmentStatus.AVAILABLE, locker.get_compartment_status("S-1"))

    def test_clear_expired_deposits(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(1, 0, 0, clock=clock, token_ttl=timedelta(minutes=1))

        token = locker.deposit_package(PackageSize.SMALL)
        clock.advance(timedelta(minutes=2))
        self.assertEqual(1, locker.clear_expired_deposits())
        self.assertFalse(locker.pickup(token))


if __name__ == '__main__':
    unittest.main()
