from dataclasses import dataclass
from enum import Enum
from typing import List


class ConsistencyLevel(Enum):
    EVENTUAL = "EVENTUAL"
    STRONG = "STRONG"


@dataclass
class SystemRequirements:
    throughput_tps: int
    read_write_ratio: float  # e.g., 10.0 means 10 reads per 1 write
    latency_sla_ms: int
    consistency_level: ConsistencyLevel


class PatternEvaluator:
    def evaluate(self, req: SystemRequirements) -> List[str]:
        patterns = []

        # High read ratio with acceptable eventual consistency or strict latency
        if req.read_write_ratio > 5.0 and req.latency_sla_ms < 50:
            patterns.append("Cache-Aside")

        # Heavy writes
        if req.read_write_ratio < 0.5 and req.throughput_tps > 10000:
            if req.consistency_level == ConsistencyLevel.EVENTUAL:
                patterns.append("Write-Behind")
            else:
                patterns.append("Event Sourcing")

        # High throughput, low latency, heavy writes -> Async processing
        if req.throughput_tps > 10000 and req.latency_sla_ms > 100:
            patterns.append("Message Queue / Worker Pool")
            
        # Very high throughput, eventual consistency
        if req.throughput_tps > 50000 and req.consistency_level == ConsistencyLevel.EVENTUAL:
             patterns.append("CQRS")

        # Strict consistency required with distributed system characteristics
        if req.consistency_level == ConsistencyLevel.STRONG and req.throughput_tps < 5000:
            patterns.append("2PC (Two-Phase Commit)")
            
        # Read heavy, very low latency
        if req.read_write_ratio > 100 and req.latency_sla_ms < 20:
             patterns.append("CDN")

        if not patterns:
            patterns.append("Standard 3-Tier Architecture")

        return patterns
