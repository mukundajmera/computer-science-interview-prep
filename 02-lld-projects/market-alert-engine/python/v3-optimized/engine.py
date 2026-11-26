import threading
import queue
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

try:
    from .models import Tick, AlertRule, Sink
except (ImportError, ValueError):
    from models import Tick, AlertRule, Sink

class AlertEngine:
    def __init__(self, max_queue_size=100000, num_workers=4):
        self.rules_by_symbol: Dict[str, List[AlertRule]] = {}
        self.last_alert_times: Dict[str, int] = {}
        
        # Locks to protect the maps in concurrent environments
        self.rules_lock = threading.Lock()
        self.cooldown_lock = threading.Lock()
        
        # Low-latency tick ingestion queue
        self.tick_queue = queue.Queue(maxsize=max_queue_size)
        self.is_running = True
        
        # Dispatcher thread pool for multi-sink asynchronous execution
        self.sink_executor = ThreadPoolExecutor(max_workers=num_workers)
        
        # Worker thread to consume ticks without blocking ingest
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.is_running = False
        self.tick_queue.put(None)  # Poison pill
        self.worker_thread.join()
        self.sink_executor.shutdown(wait=True)

    def add_rule(self, rule: AlertRule):
        with self.rules_lock:
            if rule.symbol not in self.rules_by_symbol:
                self.rules_by_symbol[rule.symbol] = []
            self.rules_by_symbol[rule.symbol].append(rule)

    def process_tick(self, tick: Tick):
        """Non-blocking ingest into the concurrent queue."""
        try:
            self.tick_queue.put_nowait(tick)
        except queue.Full:
            pass # Dropped tick if queue is full, realistically we'd log or alert

    def _worker_loop(self):
        while self.is_running:
            tick = self.tick_queue.get()
            if tick is None:
                break
            self._process_tick_internal(tick)
            self.tick_queue.task_done()

    def _process_tick_internal(self, tick: Tick):
        with self.rules_lock:
            rules = self.rules_by_symbol.get(tick.symbol, [])
        
        for rule in rules:
            if rule.condition.evaluate(tick):
                cooldown_key = f"{rule.rule_id}-{tick.symbol}"
                current_time = tick.timestamp
                
                with self.cooldown_lock:
                    last_time = self.last_alert_times.get(cooldown_key)
                    
                    if last_time is None or (current_time - last_time >= rule.cooldown_ms):
                        self.last_alert_times[cooldown_key] = current_time
                        should_dispatch = True
                    else:
                        should_dispatch = False
                
                if should_dispatch:
                    self._dispatch_alert(rule, tick)

    def _dispatch_alert(self, rule: AlertRule, tick: Tick):
        """Dispatch asynchronously to prevent blocking the worker loop."""
        for sink in rule.sinks:
            self.sink_executor.submit(sink.send, rule, tick)
