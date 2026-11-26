from enum import Enum
from typing import List, Dict, Any, Set
from collections import deque
import time


class RemediationAction(Enum):
    PASS = "PASS"
    CHALLENGE_SILENT_POW = "CHALLENGE_SILENT_POW"
    CHALLENGE_CAPTCHA = "CHALLENGE_CAPTCHA"
    BLOCK = "BLOCK"
    SHADOW_BLOCK = "SHADOW_BLOCK"


class BotRiskResponse:
    def __init__(self, risk_score: float, confidence: float, action: RemediationAction, reasons: List[str], policy_version: str, queued_for_investigation: bool):
        self.risk_score = risk_score
        self.confidence = confidence
        self.action = action
        self.reasons = reasons
        self.policy_version = policy_version
        self.queued_for_investigation = queued_for_investigation


class Event:
    def __init__(self, account_id: str, action: str, context: Dict[str, Any], timestamp: int):
        self.account_id = account_id
        self.action = action
        self.context = context if context else {}
        self.timestamp = timestamp


class InvestigationTask:
    def __init__(self, account_id: str, risk_score: float, reasons: List[str], timestamp: int):
        self.account_id = account_id
        self.risk_score = risk_score
        self.reasons = reasons
        self.timestamp = timestamp


class AuditLog:
    def __init__(self, event: Event, response: BotRiskResponse, timestamp: int):
        self.event = event
        self.response = response
        self.timestamp = timestamp


class DistributedBotDetectionPlatformService:
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = list(cluster_nodes)

        # Mock Kafka sink
        self.kafka_audit_telemetry_sink: deque = deque()
        self.investigation_queue: deque = deque()

        # Rate limiting properties
        self.account_velocity_counters: Dict[str, Dict[int, int]] = {}
        self.leaky_buckets: Dict[str, float] = {}
        self.last_leak_times: Dict[str, int] = {}
        self.bucket_capacity = 100.0
        self.leak_rate_per_ms = 100.0 / 60000.0

        # Mock Redis Cluster for global IP reputation and sync
        self.redis_ip_reputation_store: Dict[str, float] = {}

        # Mock Bloom Filter for quick global blocked IP checks
        self.bloom_filter_blocked_ips: Set[str] = set()

        self.ml_service_available = True
        self.shadow_mode_enabled = False

    def set_shadow_mode_enabled(self, enabled: bool):
        self.shadow_mode_enabled = enabled

    def set_ml_service_available(self, available: bool):
        self.ml_service_available = available

    def update_global_ip_reputation(self, ip: str, score: float):
        self.redis_ip_reputation_store[ip] = score
        if score >= 0.8:
            self.bloom_filter_blocked_ips.add(ip)
        else:
            self.bloom_filter_blocked_ips.discard(ip)

    def get_global_ip_reputation(self, ip: str) -> float:
        return self.redis_ip_reputation_store.get(ip, 0.0)

    def check_cluster_consensus(self) -> bool:
        required_majority = (len(self.cluster_nodes) // 2) + 1
        active_nodes = 1
        for node in self.cluster_nodes:
            if node != self.node_id:
                active_nodes += 1
        return active_nodes >= required_majority

    def _record_velocity(self, account_id: str, timestamp: int):
        bucket = timestamp // 1000
        if account_id not in self.account_velocity_counters:
            self.account_velocity_counters[account_id] = {}

        counters = self.account_velocity_counters[account_id]
        counters[bucket] = counters.get(bucket, 0) + 1

        one_minute_ago = (timestamp - 60000) // 1000
        # clean up old buckets
        keys_to_remove = [k for k in counters.keys() if k < one_minute_ago]
        for k in keys_to_remove:
            del counters[k]

    def _get_recent_events_count(self, account_id: str, timestamp: int) -> int:
        counters = self.account_velocity_counters.get(account_id)
        if not counters:
            return 0

        one_minute_ago = (timestamp - 60000) // 1000
        return sum(v for k, v in counters.items() if k >= one_minute_ago)

    def _check_rate_limit(self, account_id: str, timestamp: int) -> bool:
        last_time = self.last_leak_times.get(account_id, timestamp)
        tokens = self.leaky_buckets.get(account_id, self.bucket_capacity)

        time_passed = timestamp - last_time
        if time_passed > 0:
            tokens += time_passed * self.leak_rate_per_ms
            if tokens > self.bucket_capacity:
                tokens = self.bucket_capacity

        if tokens >= 1.0:
            tokens -= 1.0
            self.leaky_buckets[account_id] = tokens
            self.last_leak_times[account_id] = timestamp
            return False
        else:
            self.leaky_buckets[account_id] = tokens
            self.last_leak_times[account_id] = timestamp
            return True

    def evaluate(self, current_event: Event) -> BotRiskResponse:
        now = current_event.timestamp
        account_id = current_event.account_id
        ip = current_event.context.get("ip", "")

        self._record_velocity(account_id, now)
        is_rate_limited = self._check_rate_limit(account_id, now)
        recent_events_count = self._get_recent_events_count(account_id, now)
        velocity_score = min(1.0, recent_events_count / 50.0)

        # Fast path check using Bloom Filter
        if ip in self.bloom_filter_blocked_ips:
            ip_rep_score = 1.0
        else:
            ip_rep_score = self.redis_ip_reputation_store.get(ip, 0.0)

        device_id = current_event.context.get("device_id", "")
        device_entropy_score = 0.8 if not device_id else (0.5 if len(device_id) < 5 else 0.1)

        reasons = []
        if self.ml_service_available:
            risk_score = (velocity_score * 0.3) + (ip_rep_score * 0.6) + (device_entropy_score * 0.1)
            confidence = 0.5 + (min(recent_events_count, 100) / 200.0)
        else:
            risk_score = max(velocity_score, ip_rep_score)
            confidence = 0.4
            reasons.append("degraded_rule_mode")

        if is_rate_limited:
            risk_score = max(risk_score, 0.85)
            reasons.append("rate_limited")

        risk_score = min(1.0, max(0.0, risk_score))

        if velocity_score > 0.6:
            reasons.append("velocity_spike")
        if ip_rep_score > 0.6:
            reasons.append("bad_ip_reputation")
        if device_entropy_score > 0.6:
            reasons.append("device_anomaly")

        queue_for_investigation = False

        if risk_score >= 0.8:
            action = RemediationAction.SHADOW_BLOCK if self.shadow_mode_enabled else RemediationAction.BLOCK
        elif risk_score >= 0.6:
            action = RemediationAction.CHALLENGE_CAPTCHA
            queue_for_investigation = True
        elif risk_score >= 0.4:
            action = RemediationAction.CHALLENGE_SILENT_POW
        else:
            action = RemediationAction.PASS

        if queue_for_investigation:
            self.investigation_queue.append(InvestigationTask(account_id, risk_score, reasons, now))

        response = BotRiskResponse(risk_score, confidence, action, reasons, "v3-distributed-policy", queue_for_investigation)

        # Push to Kafka audit telemetry sink
        self.kafka_audit_telemetry_sink.append(AuditLog(current_event, response, now))

        return response
