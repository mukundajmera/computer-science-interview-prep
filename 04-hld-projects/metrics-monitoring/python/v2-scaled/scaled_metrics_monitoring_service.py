import math
from typing import Dict, List, Optional
from enum import Enum
from collections import defaultdict


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


class Resolution(Enum):
    RAW = "RAW"
    ONE_MIN = "ONE_MIN"
    ONE_HOUR = "ONE_HOUR"


class RollupPoint:
    def __init__(self, name: str, tags: Dict[str, str], resolution: Resolution, window_start_ms: int,
                 count: int, sum_value: float, min_value: float, max_value: float):
        self.name = name
        self.tags = tags.copy() if tags else {}
        self.resolution = resolution
        self.window_start_ms = window_start_ms
        self.count = count
        self.sum_value = sum_value
        self.min_value = min_value
        self.max_value = max_value


class AlertRule:
    def __init__(self, rule_id: str, metric_name: str, threshold: float, greater_than: bool,
                 hysteresis: float = 0.0, cooldown_ms: int = 0):
        self.rule_id = rule_id
        self.metric_name = metric_name
        self.threshold = threshold
        self.greater_than = greater_than
        self.hysteresis = hysteresis
        self.cooldown_ms = cooldown_ms


class AlertStatus(Enum):
    FIRING = "FIRING"
    RESOLVED = "RESOLVED"


class AlertEvent:
    def __init__(self, rule_id: str, status: AlertStatus, timestamp_ms: int):
        self.rule_id = rule_id
        self.status = status
        self.timestamp_ms = timestamp_ms


class ScaledMetricsMonitoringService:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.ingestion_buffer: List[MetricPoint] = []

        self.raw_data: List[MetricPoint] = []
        self.rollups_1m: List[RollupPoint] = []
        self.rollups_1h: List[RollupPoint] = []

        self.alert_rules: Dict[str, AlertRule] = {}
        self.current_alert_states: Dict[str, AlertStatus] = {}
        self.last_alert_time: Dict[str, int] = {}
        self.alert_history: List[AlertEvent] = []

    def ingest(self, point: MetricPoint):
        self.ingestion_buffer.append(point)
        if len(self.ingestion_buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.ingestion_buffer:
            return

        # Add to raw data
        self.raw_data.extend(self.ingestion_buffer)

        # Build rollups
        self._build_rollups(self.ingestion_buffer)

        self.ingestion_buffer.clear()

    def _get_series_key(self, name: str, tags: Dict[str, str]) -> str:
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}|{tag_str}"

    def _build_rollups(self, points: List[MetricPoint]):
        # Group by 1 minute windows (60000 ms) and 1 hour windows (3600000 ms)
        for point in points:
            window_1m = (point.timestamp_ms // 60000) * 60000
            self._update_rollup(self.rollups_1m, Resolution.ONE_MIN, point, window_1m)

            window_1h = (point.timestamp_ms // 3600000) * 3600000
            self._update_rollup(self.rollups_1h, Resolution.ONE_HOUR, point, window_1h)

    def _update_rollup(self, rollups_list: List[RollupPoint], resolution: Resolution, point: MetricPoint, window_start: int):
        # Find existing rollup or create new
        for rollup in reversed(rollups_list):
            if rollup.name == point.name and rollup.window_start_ms == window_start and self._matches_tags(rollup.tags, point.tags):
                rollup.count += 1
                rollup.sum_value += point.value
                rollup.min_value = min(rollup.min_value, point.value)
                rollup.max_value = max(rollup.max_value, point.value)
                return

        # Not found, create new
        rollups_list.append(RollupPoint(
            name=point.name,
            tags=point.tags,
            resolution=resolution,
            window_start_ms=window_start,
            count=1,
            sum_value=point.value,
            min_value=point.value,
            max_value=point.value
        ))

    def query_range(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int, resolution: Resolution = Resolution.RAW):
        # Ensure flushed before query to be fully consistent (or we could just query buffer + raw)
        self.flush()

        result = []
        if resolution == Resolution.RAW:
            source = self.raw_data
            for p in source:
                if p.name == metric_name and start_ms <= p.timestamp_ms <= end_ms:
                    if self._matches_tags(p.tags, tags):
                        result.append(p)
        elif resolution == Resolution.ONE_MIN:
            source = self.rollups_1m
            for p in source:
                if p.name == metric_name and start_ms <= p.window_start_ms <= end_ms:
                    if self._matches_tags(p.tags, tags):
                        result.append(p)
        elif resolution == Resolution.ONE_HOUR:
            source = self.rollups_1h
            for p in source:
                if p.name == metric_name and start_ms <= p.window_start_ms <= end_ms:
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
        self.flush()
        new_events = []

        for rule in self.alert_rules.values():
            latest = None
            for p in reversed(self.raw_data):
                if p.name == rule.metric_name:
                    latest = p
                    break

            if latest is not None:
                current_state = self.current_alert_states.get(rule.rule_id, AlertStatus.RESOLVED)
                last_time = self.last_alert_time.get(rule.rule_id, 0)

                # Check cooldown (only apply if last_time != 0)
                if last_time != 0 and current_timestamp_ms - last_time < rule.cooldown_ms:
                    continue

                if rule.greater_than:
                    # Fire if value > threshold
                    # Resolve if value < threshold - hysteresis
                    is_firing = latest.value > rule.threshold
                    is_resolving = latest.value < (rule.threshold - rule.hysteresis)
                else:
                    # Fire if value < threshold
                    # Resolve if value > threshold + hysteresis
                    is_firing = latest.value < rule.threshold
                    is_resolving = latest.value > (rule.threshold + rule.hysteresis)

                if is_firing and current_state == AlertStatus.RESOLVED:
                    self.current_alert_states[rule.rule_id] = AlertStatus.FIRING
                    self.last_alert_time[rule.rule_id] = current_timestamp_ms
                    event = AlertEvent(rule.rule_id, AlertStatus.FIRING, current_timestamp_ms)
                    self.alert_history.append(event)
                    new_events.append(event)
                elif is_resolving and current_state == AlertStatus.FIRING:
                    self.current_alert_states[rule.rule_id] = AlertStatus.RESOLVED
                    self.last_alert_time[rule.rule_id] = current_timestamp_ms
                    event = AlertEvent(rule.rule_id, AlertStatus.RESOLVED, current_timestamp_ms)
                    self.alert_history.append(event)
                    new_events.append(event)

        return new_events

    def get_sliding_window_percentile(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int, percentile: float) -> float:
        self.flush()
        points = [p for p in self.raw_data if p.name == metric_name and p.metric_type == MetricType.HISTOGRAM and start_ms <= p.timestamp_ms <= end_ms and self._matches_tags(p.tags, tags)]
        if not points:
            return 0.0

        values = sorted([p.value for p in points])
        index = int(math.ceil((percentile / 100.0) * len(values))) - 1
        index = max(0, min(index, len(values) - 1))
        return values[index]
