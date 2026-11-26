import threading
import time
from typing import Dict, Any

class RedisSimulator:
    """
    Simulates a central Redis store that processes commands atomically using a lock
    to mimic the single-threaded nature of Redis.
    """
    def __init__(self):
        self.store = {}
        self.lock = threading.RLock()
    
    def eval_lua(self, script_name: str, keys: list, args: list) -> Any:
        with self.lock:
            if script_name == "reserve_batch":
                return self._reserve_batch(keys, args)
            elif script_name == "sliding_window_increment":
                return self._sliding_window_increment(keys, args)
            raise ValueError(f"Unknown script: {script_name}")
            
    def _reserve_batch(self, keys, args):
        """
        keys: [user_key]
        args: [global_limit, batch_size, window_seconds, current_timestamp]
        """
        user_key = keys[0]
        global_limit = int(args[0])
        batch_size = int(args[1])
        window_sec = int(args[2])
        now = int(args[3])
        
        # Calculate current window based on time
        current_window_key = f"{user_key}:{now // window_sec}"
        
        # We simplify by just tracking a counter for the current window 
        # (This acts as a basic fixed window limit for the global pool in this simulation, 
        # but represents the centralized quota exhaustion part).
        current_usage = self.store.get(current_window_key, 0)
        
        if current_usage >= global_limit:
            return 0  # Rejected
            
        # Allocate up to batch_size
        available = global_limit - current_usage
        allocated = min(batch_size, available)
        
        self.store[current_window_key] = current_usage + allocated
        return allocated

    def _sliding_window_increment(self, keys, args):
        """
        Atomic sliding window counter approximation decrement/increment logic.
        This simulates a purely Redis-backed sliding window counter without local batching.
        keys: [user_key]
        args: [limit, window_sec, current_timestamp]
        """
        user_key = keys[0]
        limit = int(args[0])
        window_sec = int(args[1])
        now = int(args[2])
        
        current_window_start = (now // window_sec) * window_sec
        prev_window_start = current_window_start - window_sec
        
        curr_key = f"{user_key}:{current_window_start}"
        prev_key = f"{user_key}:{prev_window_start}"
        
        curr_count = self.store.get(curr_key, 0)
        prev_count = self.store.get(prev_key, 0)
        
        elapsed_in_window = now - current_window_start
        weight = 1.0 - (elapsed_in_window / float(window_sec))
        
        estimated_count = int(prev_count * weight) + curr_count
        
        if estimated_count >= limit:
            return 0 # Rejected
            
        self.store[curr_key] = curr_count + 1
        return 1 # Allowed


class Tier1DistributedRateLimiter:
    """
    Implements Local Memory Token Batching architecture backed by a central Redis simulator.
    """
    def __init__(self, redis: RedisSimulator, global_limit: int, window_sec: int, batch_size: int):
        self.redis = redis
        self.global_limit = global_limit
        self.window_sec = window_sec
        self.batch_size = batch_size
        
        # Local state
        self.local_tokens = {} # user_id -> token count
        self.lock = threading.RLock()
        
        # Background replenishment simulation
        # In a real system this would be a thread pool or async tasks
        # For simulation, we'll allow an inline fetch if local is exhausted,
        # but in test we'll verify it serves from local memory directly when tokens are present.
        
    def allow_request(self, user_id: str, current_time: int) -> bool:
        """
        Attempts to allow a request, utilizing local memory token batching.
        """
        with self.lock:
            tokens = self.local_tokens.get(user_id, 0)
            
            if tokens > 0:
                # Fast path: consume local token
                self.local_tokens[user_id] -= 1
                
                # In real life, trigger async fetch if tokens < threshold
                if self.local_tokens[user_id] < self.batch_size * 0.2:
                    self._trigger_async_replenish(user_id, current_time)
                
                return True
                
            # If 0 tokens, we must fetch synchronously to serve this request
            # (or fail closed/open depending on config. Here we try to fetch)
            fetched = self._fetch_batch(user_id, current_time)
            if fetched > 0:
                # Consume one immediately
                self.local_tokens[user_id] = fetched - 1
                return True
                
            return False

    def _trigger_async_replenish(self, user_id: str, current_time: int):
        """Simulates an asynchronous background fetch (runs inline for predictability in simple simulation unless true threading is used)"""
        # For a truly async simulation in Python tests, we might use a thread,
        # but for simplicity we simulate it synchronously or just queue it.
        # We will just fetch it here.
        fetched = self._fetch_batch(user_id, current_time)
        if fetched > 0:
            self.local_tokens[user_id] = self.local_tokens.get(user_id, 0) + fetched

    def _fetch_batch(self, user_id: str, current_time: int) -> int:
        """Calls the central Redis store to fetch a batch of tokens."""
        return self.redis.eval_lua(
            "reserve_batch", 
            [user_id], 
            [self.global_limit, self.batch_size, self.window_sec, current_time]
        )
