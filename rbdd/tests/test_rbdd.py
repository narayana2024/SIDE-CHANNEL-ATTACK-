"""End-to-end tests for the RBDD Framework Orchestrator."""

import pytest
from src.models.rbdd import RBDDFramework
from src.data.page_matrix import PageMatrix
from src.data.access_traces import AccessTrace, TraceEntry

@pytest.fixture
def framework():
    return RBDDFramework(abm_threshold=0.8, blrm_threshold=0.6, block_size=10)

def test_full_pipeline_allowed_user(framework):
    at = AccessTrace()
    pm = PageMatrix()
    
    # Setup allowed user u1
    for i in range(10):
        at.add_trace(TraceEntry("u1", f"b{i%2}", "update", "now", "success", True, True))
        
    data = b"0123456789" # One block
    ukey = b"user_key_exactly_32_bytes_long!!"
    
    # 1. First upload (Unique)
    res1 = framework.process_request("u1", data, "upload", at, pm, ukey)
    assert res1["status"] == "COMPLETED"
    assert res1["unique"] == 1
    assert len(pm) == 1
    
    # 2. Second upload of same data (Duplicate)
    res2 = framework.process_request("u1", data, "upload", at, pm, ukey)
    assert res2["status"] == "COMPLETED"
    assert res2["duplicates"] == 1
    assert res2["unique"] == 0
    assert len(pm) == 1 # Still 1 in matrix

def test_full_pipeline_denied_user(framework):
    at = AccessTrace()
    pm = PageMatrix()
    
    # Setup malicious user u2 (all failures)
    for i in range(10):
        at.add_trace(TraceEntry("u2", "b1", "update", "now", "fail", False, False))
        
    data = b"secret_data"
    ukey = b"key" * 8
    
    res = framework.process_request("u2", data, "upload", at, pm, ukey)
    assert res["status"] == "REJECTED"
    assert len(pm) == 0

def test_time_complexity_measurement(framework):
    # Just ensure it runs without error
    time_taken = framework.measure_time_complexity(num_blocks=5, user_id="test")
    assert time_taken > 0

def test_simulation_run(framework):
    users = [
        {"user_id": "legit", "type": "legitimate"},
        {"user_id": "bad", "type": "malicious"}
    ]
    # Traces to make 'legit' allowed and 'bad' denied
    at = AccessTrace()
    for _ in range(5):
        at.add_trace(TraceEntry("legit", "b1", "update", "now", "success", True, True))
        at.add_trace(TraceEntry("bad", "b1", "update", "now", "fail", False, False))
    
    blocks = [b"data" * 10] * 5
    metrics = framework.run_simulation(users, blocks, at)
    
    assert "restriction" in metrics
    assert "deduplication" in metrics
    assert "encryption" in metrics
    # with 5 identical blocks, deduplication should be high
    assert metrics["deduplication"] > 0
