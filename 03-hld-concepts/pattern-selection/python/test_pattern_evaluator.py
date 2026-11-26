import pytest
from pattern_evaluator import SystemRequirements, ConsistencyLevel, PatternEvaluator

def test_cache_aside_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=5000,
        read_write_ratio=10.0,
        latency_sla_ms=40,
        consistency_level=ConsistencyLevel.EVENTUAL
    )
    patterns = evaluator.evaluate(req)
    assert "Cache-Aside" in patterns

def test_write_behind_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=15000,
        read_write_ratio=0.1,
        latency_sla_ms=200,
        consistency_level=ConsistencyLevel.EVENTUAL
    )
    patterns = evaluator.evaluate(req)
    assert "Write-Behind" in patterns
    assert "Message Queue / Worker Pool" in patterns

def test_event_sourcing_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=15000,
        read_write_ratio=0.1,
        latency_sla_ms=200,
        consistency_level=ConsistencyLevel.STRONG
    )
    patterns = evaluator.evaluate(req)
    assert "Event Sourcing" in patterns
    assert "Message Queue / Worker Pool" in patterns

def test_two_phase_commit_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=1000,
        read_write_ratio=1.0,
        latency_sla_ms=500,
        consistency_level=ConsistencyLevel.STRONG
    )
    patterns = evaluator.evaluate(req)
    assert "2PC (Two-Phase Commit)" in patterns

def test_cqrs_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=60000,
        read_write_ratio=2.0,
        latency_sla_ms=200,
        consistency_level=ConsistencyLevel.EVENTUAL
    )
    patterns = evaluator.evaluate(req)
    assert "CQRS" in patterns
    assert "Message Queue / Worker Pool" in patterns

def test_cdn_pattern():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=5000,
        read_write_ratio=200.0,
        latency_sla_ms=10,
        consistency_level=ConsistencyLevel.EVENTUAL
    )
    patterns = evaluator.evaluate(req)
    assert "CDN" in patterns
    assert "Cache-Aside" in patterns

def test_standard_architecture_fallback():
    evaluator = PatternEvaluator()
    req = SystemRequirements(
        throughput_tps=100,
        read_write_ratio=1.0,
        latency_sla_ms=500,
        consistency_level=ConsistencyLevel.EVENTUAL
    )
    patterns = evaluator.evaluate(req)
    assert patterns == ["Standard 3-Tier Architecture"]
