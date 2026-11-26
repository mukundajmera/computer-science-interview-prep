"""
V3: Alerting System with Threshold Detection

Monitors metrics and fires alerts when thresholds are breached.
"""

import time
import threading
from typing import Dict, List, Callable
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Comparator(Enum):
    GREATER_THAN = ("gt", lambda a, b: a > b)
    LESS_THAN = ("lt", lambda a, b: a < b)
    
    def __init__(self, symbol: str, predicate: Callable[[float, float], bool]):
        self.symbol = symbol
        self._predicate = predicate
    
    def test(self, a: float, b: float) -> bool:
        return self._predicate(a, b)


@dataclass
class Alert:
    """An alert event."""
    rule_name: str
    severity: Severity
    message: str
    timestamp: float


@dataclass
class AlertRule:
    """Rule for triggering alerts."""
    name: str
    metric_name: str
    value_type: str  # 'avg', 'max', 'p99', 'count'
    comparator: Comparator
    threshold: float
    severity: Severity


@dataclass
class MetricStats:
    count: int
    min: float
    max: float
    avg: float
    p99: float


class SimpleMetrics:
    """Simple metrics store for alerting."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, name: str, value: float) -> None:
        with self._lock:
            self._metrics[name].append(value)

    def get_stats(self, name: str) -> MetricStats:
        with self._lock:
            values = self._metrics.get(name, [])
            if not values:
                return MetricStats(0, 0, 0, 0, 0)
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            return MetricStats(
                count=count,
                min=sorted_values[0],
                max=sorted_values[-1],
                avg=sum(sorted_values) / count,
                p99=sorted_values[int(count * 0.99)] if count > 0 else 0
            )


class AlertingSystem:
    """
    Alerting system with threshold detection.
    
    Example:
        metrics = SimpleMetrics()
        alerting = AlertingSystem(metrics)
        alerting.add_rule(AlertRule(
            name="HighLatency",
            metric_name="latency",
            value_type="p99",
            comparator=Comparator.GREATER_THAN,
            threshold=200.0,
            severity=Severity.WARNING
        ))
        alerting.add_handler(lambda alert: print(alert))
        alerting.start(check_interval_seconds=1)
    """
    
    def __init__(self, metrics: SimpleMetrics):
        self._metrics = metrics
        self._rules: List[AlertRule] = []
        self._handlers: List[Callable[[Alert], None]] = []
        self._running = False
        self._thread = None

    def add_rule(self, rule: AlertRule) -> None:
        self._rules.append(rule)

    def add_handler(self, handler: Callable[[Alert], None]) -> None:
        self._handlers.append(handler)

    def start(self, check_interval_seconds: float = 1.0) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(check_interval_seconds,),
            daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run_loop(self, interval: float) -> None:
        while self._running:
            self._check_rules()
            time.sleep(interval)

    def _check_rules(self) -> None:
        for rule in self._rules:
            stats = self._metrics.get_stats(rule.metric_name)
            value = self._get_value_for_type(stats, rule.value_type)
            
            if rule.comparator.test(value, rule.threshold):
                alert = Alert(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"{rule.metric_name} {rule.value_type}: {value:.2f} {rule.comparator.symbol} {rule.threshold}",
                    timestamp=time.time()
                )
                self._fire_alert(alert)

    def _get_value_for_type(self, stats: MetricStats, value_type: str) -> float:
        return {
            'avg': stats.avg,
            'max': stats.max,
            'p99': stats.p99,
            'count': float(stats.count),
        }.get(value_type, stats.avg)

    def _fire_alert(self, alert: Alert) -> None:
        for handler in self._handlers:
            handler(alert)


if __name__ == "__main__":
    import random
    
    metrics = SimpleMetrics()
    alerting = AlertingSystem(metrics)
    
    alerting.add_rule(AlertRule(
        name="HighLatency",
        metric_name="latency",
        value_type="p99",
        comparator=Comparator.GREATER_THAN,
        threshold=200.0,
        severity=Severity.WARNING
    ))
    
    alerting.add_handler(lambda alert: 
        print(f"[{alert.severity.value}] {alert.rule_name}: {alert.message}"))
    
    # Record metrics
    for _ in range(100):
        metrics.record("latency", random.gauss(150, 50))
    
    alerting.start(check_interval_seconds=1)
    time.sleep(3)
    alerting.stop()
