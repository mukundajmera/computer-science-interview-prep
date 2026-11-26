import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pacelc_simulator import PacelcSimulator

def test_pcec_rejects_minority():
    simulator = PacelcSimulator("PC_EC")
    simulator.injectPartition([2, 3])
    res = simulator.write("k1", "v1")
    assert res["status"] == "error"
    assert "Minority partition" in res["message"]

def test_pcel_normal_fast_but_rejects_minority():
    simulator = PacelcSimulator("PC_EL")
    res = simulator.write("k1", "v1")
    assert res["status"] == "success"
    assert res["latency"] < 0.05

    simulator.injectPartition([2, 3])
    res2 = simulator.write("k1", "v2")
    assert res2["status"] == "error"
    assert "Minority partition" in res2["message"]

def test_pael_accepts_fast_writes_and_converges():
    simulator = PacelcSimulator("PA_EL")
    res1 = simulator.write("k1", "v1")
    assert res1["status"] == "success"
    assert res1["latency"] < 0.05
    
    simulator.injectPartition([2, 3])
    res2 = simulator.write("k1", "v2")
    assert res2["status"] == "success"
    
    assert simulator.nodes[2] == "v1"
    assert simulator.nodes[3] == "v1"
    
    simulator.healPartition()
    assert simulator.nodes[1] == simulator.nodes[2]
    assert simulator.nodes[2] == simulator.nodes[3]

def test_invalid_policy_rejection():
    with pytest.raises(ValueError) as excinfo:
        PacelcSimulator("INVALID_POLICY")
    assert "Invalid policy" in str(excinfo.value)
