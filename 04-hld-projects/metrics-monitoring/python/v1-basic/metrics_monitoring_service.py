import math
from typing import Dict, List, Optional
from enum import Enum


class MetricType(Enum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"


class MetricPoint:
    def __init__(self, name: str, metric_type: MetricType, tags: Dict[str, str], timestamp_ms: int, value: float):
        self.name = name
        self.metric_type = metric_type
        self.tags = tags.copy() if tags else {}
        self.timestamp_ms = timestamp_ms
        self.value = value


class AlertRule:
    def __init__(self, rule_id: str, metric_name: str, threshold: float, greater_than: bool):
        self.rule_id = rule_id
        self.metric_name = metric_name
        self.threshold = threshold
        self.greater_than = greater_than


class AlertStatus(Enum):
    FIRING = "FIRING"
    RESOLVED = "RESOLVED"


class AlertEvent:
    def __init__(self, rule_id: str, status: AlertStatus, timestamp_ms: int):
        self.rule_id = rule_id
        self.status = status
        self.timestamp_ms = timestamp_ms


class MetricsMonitoringService:
    def __init__(self):
        self.data_store: List[MetricPoint] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.current_alert_states: Dict[str, AlertStatus] = {}
        self.alert_history: List[AlertEvent] = []

    def ingest(self, point: MetricPoint):
        self.data_store.append(point)

    def query_range(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> List[MetricPoint]:
        result = []
        for p in self.data_store:
            if p.name == metric_name and start_ms <= p.timestamp_ms <= end_ms:
                if self._matches_tags(p.tags, tags):
                    result.append(p)
        return result

    def _matches_tags(self, point_tags: Dict[str, str], query_tags: Dict[str, str]) -> bool:
        if not query_tags:
            return True
        for k, v in query_tags.items():
            if point_tags.get(k) != v:
                return False
        return True

    def register_alert_rule(self, rule: AlertRule):
        self.alert_rules[rule.rule_id] = rule
        self.current_alert_states[rule.rule_id] = AlertStatus.RESOLVED

    def evaluate_alerts(self, current_timestamp_ms: int) -> List[AlertEvent]:
        new_events = []

        for rule in self.alert_rules.values():
            latest = None
            for p in reversed(self.data_store):
                if p.name == rule.metric_name:
                    latest = p
                    break

            if latest is not None:
                is_firing = latest.value > rule.threshold if rule.greater_than else latest.value < rule.threshold
                current_state = self.current_alert_states.get(rule.rule_id, AlertStatus.RESOLVED)

                if is_firing and current_state == AlertStatus.RESOLVED:
                    self.current_alert_states[rule.rule_id] = AlertStatus.FIRING
                    event = AlertEvent(rule.rule_id, AlertStatus.FIRING, current_timestamp_ms)
                    self.alert_history.append(event)
                    new_events.append(event)
                elif not is_firing and current_state == AlertStatus.FIRING:
                    self.current_alert_states[rule.rule_id] = AlertStatus.RESOLVED
                    event = AlertEvent(rule.rule_id, AlertStatus.RESOLVED, current_timestamp_ms)
                    self.alert_history.append(event)
                    new_events.append(event)

        return new_events

    def get_histogram_percentile(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int, percentile: float) -> float:
        points = [p for p in self.query_range(metric_name, tags, start_ms, end_ms) if p.metric_type == MetricType.HISTOGRAM]
        if not points:
            return 0.0

        values = sorted([p.value for p in points])
        index = int(math.ceil((percentile / 100.0) * len(values))) - 1
        index = max(0, min(index, len(values) - 1))
        return values[index]

    def get_counter_total(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> float:
        points = [p for p in self.query_range(metric_name, tags, start_ms, end_ms) if p.metric_type == MetricType.COUNTER]
        return sum(p.value for p in points)

    def get_gauge_latest(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> float:
        points = [p for p in self.query_range(metric_name, tags, start_ms, end_ms) if p.metric_type == MetricType.GAUGE]
        if not points:
            return 0.0
        return max(points, key=lambda p: p.timestamp_ms).value
