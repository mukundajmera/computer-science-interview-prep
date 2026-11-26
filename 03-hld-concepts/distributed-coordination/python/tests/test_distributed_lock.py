import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from distributed_lock import LockServer, DistributedLock

def test_acquire_and_release():
    server = LockServer()
    lock = DistributedLock(server, "resource1")

    token = lock.acquire()
    assert token is not None
    assert token > 0

    # Try acquiring by someone else
    lock2 = DistributedLock(server, "resource1", ttl=1)
    token2 = lock2.acquire(blocking=False)
    assert token2 is None

    # Release the lock
    success = lock.release()
    assert success is True

    # Now someone else can acquire
    token3 = lock2.acquire(blocking=False)
    assert token3 is not None
    assert token3 > token
    lock2.release()


def test_lock_expiration():
    server = LockServer()
    # Mocking lock without heartbeat thread for test
    client_id = "client1"
    token = server.acquire("resource1", client_id, ttl=0.5)

    assert token is not None

    # Another client trying to acquire
    client_id2 = "client2"
    token2 = server.acquire("resource1", client_id2, ttl=1)
    assert token2 is None

    # Wait for expiration
    time.sleep(0.6)

    # Now another client can acquire
    token3 = server.acquire("resource1", client_id2, ttl=1)
    assert token3 is not None
    assert token3 > token

def test_fencing_token_monotonic():
    server = LockServer()
    tokens = []
    for i in range(5):
        client_id = f"client{i}"
        token = server.acquire(f"resource{i}", client_id, ttl=10)
        tokens.append(token)

    for i in range(1, len(tokens)):
        assert tokens[i] > tokens[i-1]


def test_lock_renewal_heartbeat():
    server = LockServer()
    lock = DistributedLock(server, "resource1", ttl=1.0, heartbeat_interval=0.3)

    token = lock.acquire()
    assert token is not None

    # Wait longer than TTL
    time.sleep(1.5)

    # The heartbeat thread should have renewed the lock
    # Another client should not be able to acquire
    lock2 = DistributedLock(server, "resource1", ttl=1.0)
    token2 = lock2.acquire(blocking=False)
    assert token2 is None

    # Lock still holds
    assert lock.token == token
    lock.release()

def test_only_owner_can_release():
    server = LockServer()
    client1 = "c1"
    client2 = "c2"

    token1 = server.acquire("resource1", client1, ttl=10)

    # Client 2 tries to release client 1's lock
    success = server.release("resource1", client2, token1)
    assert success is False

    # Client 1 tries to release with wrong token
    success2 = server.release("resource1", client1, token1 + 1)
    assert success2 is False

    # Client 1 releases correctly
    success3 = server.release("resource1", client1, token1)
    assert success3 is True

def test_only_owner_can_renew():
    server = LockServer()
    client1 = "c1"
    client2 = "c2"

    token1 = server.acquire("resource1", client1, ttl=1)

    # Client 2 tries to renew client 1's lock
    success = server.renew("resource1", client2, 1, token1)
    assert success is False

    # Client 1 tries to renew correctly
    success2 = server.renew("resource1", client1, 2, token1)
    assert success2 is True
