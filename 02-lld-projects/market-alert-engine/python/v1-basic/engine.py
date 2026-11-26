import threading
from typing import Dict, List
try:
    from .models import Tick, AlertRule, Sink
except (ImportError, ValueError):
    from models import Tick, AlertRule, Sink


class AlertEngine:
    def __init__(self):
        self.rules_by_symbol: Dict[str, List[AlertRule]] = {}
        self.last_alert_times: Dict[str, int] = {}
        # Locks to protect the maps in concurrent environments
        self.rules_lock = threading.Lock()
        self.cooldown_lock = threading.Lock()

    def add_rule(self, rule: AlertRule):
        with self.rules_lock:
            if rule.symbol not in self.rules_by_symbol:
                self.rules_by_symbol[rule.symbol] = []
            self.rules_by_symbol[rule.symbol].append(rule)

    def process_tick(self, tick: Tick):
        with self.rules_lock:
            rules = self.rules_by_symbol.get(tick.symbol, [])
        
        for rule in rules:
            if rule.condition.evaluate(tick):
                cooldown_key = f"{rule.rule_id}-{tick.symbol}"
                current_time = tick.timestamp
                
                with self.cooldown_lock:
                    last_time = self.last_alert_times.get(cooldown_key)
                    
                    if last_time is None or (current_time - last_time >= rule.cooldown_ms):
                        # Safe to trigger
                        self.last_alert_times[cooldown_key] = current_time
                        should_dispatch = True
                    else:
                        should_dispatch = False
                
                if should_dispatch:
                    self._dispatch_alert(rule, tick)

    def _dispatch_alert(self, rule: AlertRule, tick: Tick):
        for sink in rule.sinks:
            sink.send(rule, tick)
