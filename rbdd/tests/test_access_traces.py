"""Tests for the AccessTrace data structure."""

import pytest
from src.data.access_traces import AccessTrace, TraceEntry

@pytest.fixture
def sample_traces():
    at = AccessTrace()
    # User 1: 5 accesses, 3 distinct blocks, 3 updates (2 compliant), 4 successful
    at.add_trace(TraceEntry("u1", "b1", "read", "2023-01-01T10:00:00", "success", True, True))
    at.add_trace(TraceEntry("u1", "b2", "update", "2023-01-01T10:05:00", "success", True, True))
    at.add_trace(TraceEntry("u1", "b2", "update", "2023-01-01T10:10:00", "fail", False, True))
    at.add_trace(TraceEntry("u1", "b3", "update", "2023-01-01T10:15:00", "success", True, True))
    at.add_trace(TraceEntry("u1", "b1", "read", "2023-01-01T10:20:00", "success", True, True))
    
    # User 2: 2 accesses
    at.add_trace(TraceEntry("u2", "b1", "read", "2023-01-01T11:00:00", "success", True, True))
    at.add_trace(TraceEntry("u2", "b1", "read", "2023-01-01T11:05:00", "success", True, True))
    return at

def test_total_access_count(sample_traces):
    assert sample_traces.get_total_access_count("u1") == 5
    assert sample_traces.get_total_access_count("u2") == 2

def test_distinct_blocks(sample_traces):
    assert sample_traces.get_distinct_blocks_accessed("u1") == 3
    assert sample_traces.get_distinct_blocks_accessed("u2") == 1

def test_total_updates(sample_traces):
    assert sample_traces.get_total_updates("u1") == 3
    assert sample_traces.get_total_updates("u2") == 0

def test_compliant_updates(sample_traces):
    # u1 format_ok=False for one update
    assert sample_traces.get_protocol_compliant_updates("u1") == 2
    assert sample_traces.get_protocol_compliant_updates("u2") == 0

def test_successful_accesses(sample_traces):
    assert sample_traces.get_successful_accesses("u1") == 4
    assert sample_traces.get_successful_accesses("u2") == 2

def test_get_user_traces(sample_traces):
    traces = sample_traces.get_user_traces("u1")
    assert len(traces) == 5
    assert all(t.user_id == "u1" for t in traces)
