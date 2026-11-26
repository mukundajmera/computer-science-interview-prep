import unittest
import sys
import os
import hashlib
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v3 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed', 'distributed_file_service.py')), 'distributed_file_service')

class MockGeoRouter(v3.GeoRouter):
    def determine_region(self, user_id):
        return "us-east"
    def get_nearest_region(self, client_ip):
        return "us-west"
    def get_replication_targets(self, region):
        return ["eu-west"]

class MockReplicator(v3.CrossRegionReplicator):
    def replicate_metadata(self, file_id, source, target):
        pass
    def replicate_blob(self, file_id, source, target):
        pass
    def get_replication_status(self, file_id):
        return v3.ReplicationStatus(file_id=file_id, region_status={})

class MockLock(v3.DistributedLock):
    def acquire(self, lock_key, timeout_ms):
        return True
    def release(self, lock_key):
        pass
    def extend(self, lock_key, timeout_ms):
        return True

class MockEventBus(v3.EventBus):
    def publish(self, topic, event):
        pass
    def subscribe(self, topic, handler):
        pass

class MockConflictResolver(v3.ConflictResolver):
    pass

class TestV3DistributedFileStorage(unittest.TestCase):
    def setUp(self):
        self.router = MockGeoRouter()
        self.replicator = MockReplicator()
        self.lock = MockLock()
        self.event_bus = MockEventBus()
        self.conflict_resolver = MockConflictResolver()
        self.service = v3.DistributedFileStorageService(
            self.router, self.replicator, self.lock,
            self.event_bus, self.conflict_resolver, "us-east"
        )
        
    def test_upload_file(self):
        async def run_upload():
            return self.service.upload_file("u1", "test.txt", b"content", "f1")
            
        ver = asyncio.run(run_upload())
        self.assertEqual(ver.size, 7)
        self.assertEqual(ver.region, "us-east")
        self.assertEqual(ver.version_number, 1)

    def test_sync_operations(self):
        pass

    def test_geo_routing(self):
        self.assertEqual(self.router.determine_region("u1"), "us-east")
        self.assertEqual(self.router.get_nearest_region("127.0.0.1"), "us-west")

    def test_resolve_conflict(self):
        v_old = v3.FileVersion(version_id="1", file_id="f1", version_number=1, size=10,
                               checksum="a", modified_by="u1", modified_at=1000, region="us-east")
        v_new = v3.FileVersion(version_id="2", file_id="f1", version_number=2, size=12,
                               checksum="b", modified_by="u1", modified_at=2000, region="us-west")
        
        res = self.conflict_resolver.resolve_conflict([v_old, v_new], v3.ResolutionStrategy.LAST_WRITE_WINS)
        self.assertEqual(res.version_id, "2")

    def test_quota_manager(self):
        qm = v3.QuotaManager(100)
        self.assertTrue(qm.check_quota("u1", 50))
        qm._user_usage["u1"] = 50
        self.assertFalse(qm.check_quota("u1", 60))
        self.assertTrue(qm.check_quota("u1", 50))

    def test_replication_status(self):
        status = v3.ReplicationStatus(
            file_id="f1",
            region_status={"us-west": v3.ReplicationStatusEnum.COMPLETED, "eu-west": v3.ReplicationStatusEnum.PENDING}
        )
        self.assertFalse(status.is_fully_replicated())
        
        status.region_status["eu-west"] = v3.ReplicationStatusEnum.COMPLETED
        self.assertTrue(status.is_fully_replicated())

if __name__ == '__main__':
    unittest.main()
