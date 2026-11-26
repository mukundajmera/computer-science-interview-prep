import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
for module_name in ["locker", "package_size", "access_token", "compartment"]:
    sys.modules.pop(module_name, None)

from locker import Locker
from package_size import PackageSize


class MutableClock:
    def __init__(self, now: datetime):
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


class AmazonLockerV1Test(unittest.TestCase):
    def test_exact_deposit_and_pickup(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(1, 0, 0, clock=clock.now)

        token = locker.deposit_package(PackageSize.SMALL)
        self.assertIsNotNone(token)
        self.assertIsNone(locker.deposit_package(PackageSize.SMALL))

        self.assertTrue(locker.pickup(token))
        self.assertFalse(locker.pickup(token))

    def test_expired_token_cleanup(self):
        clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        locker = Locker(0, 1, 0, clock=clock.now, token_ttl=timedelta(hours=1))

        token = locker.deposit_package(PackageSize.MEDIUM)
        self.assertEqual(1, locker.get_active_token_count())

        clock.advance(timedelta(hours=2))
        self.assertEqual(1, locker.clear_expired_deposits())
        self.assertFalse(locker.pickup(token))


if __name__ == '__main__':
    unittest.main()
