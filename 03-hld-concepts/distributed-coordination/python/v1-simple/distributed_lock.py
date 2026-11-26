import time
import threading
import uuid

class LockServer:
    def __init__(self):
        self._locks = {}  # lock_name -> { 'owner': client_id, 'token': int, 'expires_at': float }
        self._fencing_token = 0
        self._lock = threading.Lock()

    def acquire(self, lock_name, client_id, ttl):
        with self._lock:
            now = time.time()
            if lock_name in self._locks:
                lock_info = self._locks[lock_name]
                if lock_info['expires_at'] > now and lock_info['owner'] != client_id:
                    return None # Lock is held by someone else

            # Issue or renew lock
            self._fencing_token += 1
            token = self._fencing_token

            self._locks[lock_name] = {
                'owner': client_id,
                'token': token,
                'expires_at': now + ttl
            }
            return token

    def renew(self, lock_name, client_id, ttl, token):
        with self._lock:
            now = time.time()
            if lock_name not in self._locks:
                return False

            lock_info = self._locks[lock_name]

            # Check owner and token
            if lock_info['owner'] != client_id or lock_info['token'] != token:
                return False

            if lock_info['expires_at'] < now:
                return False # Lease expired, must re-acquire

            self._locks[lock_name]['expires_at'] = now + ttl
            return True

    def release(self, lock_name, client_id, token):
        with self._lock:
            if lock_name not in self._locks:
                return False

            lock_info = self._locks[lock_name]
            if lock_info['owner'] != client_id or lock_info['token'] != token:
                return False

            del self._locks[lock_name]
            return True


class DistributedLock:
    def __init__(self, server, lock_name, ttl=5.0, heartbeat_interval=2.0):
        self.server = server
        self.lock_name = lock_name
        self.client_id = str(uuid.uuid4())
        self.ttl = ttl
        self.heartbeat_interval = heartbeat_interval

        self.token = None
        self._stop_heartbeat = threading.Event()
        self._heartbeat_thread = None
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=None):
        start_time = time.time()
        while True:
            token = self.server.acquire(self.lock_name, self.client_id, self.ttl)
            if token is not None:
                with self._lock:
                    self.token = token
                    self._stop_heartbeat.clear()
                    self._heartbeat_thread = threading.Thread(target=self._heartbeat, daemon=True)
                    self._heartbeat_thread.start()
                return token

            if not blocking:
                return None

            if timeout is not None and time.time() - start_time >= timeout:
                return None

            time.sleep(0.1)

    def _heartbeat(self):
        while not self._stop_heartbeat.is_set():
            # Wait with smaller steps to respond quickly to stop events
            slept = 0
            while slept < self.heartbeat_interval:
                if self._stop_heartbeat.is_set():
                    break
                time.sleep(0.1)
                slept += 0.1

            if self._stop_heartbeat.is_set():
                break

            with self._lock:
                if self.token is None:
                    break
                success = self.server.renew(self.lock_name, self.client_id, self.ttl, self.token)
                if not success:
                    # Lease lost
                    self.token = None
                    break

    def release(self):
        with self._lock:
            if self.token is None:
                return False

            self._stop_heartbeat.set()
            # Wait for heartbeat thread to stop if we are not on it
            if self._heartbeat_thread and self._heartbeat_thread != threading.current_thread():
                self._heartbeat_thread.join(timeout=0.5)

            success = self.server.release(self.lock_name, self.client_id, self.token)
            self.token = None
            return success
