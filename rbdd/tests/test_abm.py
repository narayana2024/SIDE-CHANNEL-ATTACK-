"""Tests for the Access Behavioral Measure (ABM) logic."""

import pytest
from src.models.abm import ABMAccessControl
from src.data.access_traces import AccessTrace, TraceEntry

@pytest.fixture
def abm_controller():
    return ABMAccessControl(threshold=0.8)

@pytest.fixture
def access_data():
    at = AccessTrace()
    
    # User 1: High success, high updates, high compliance (Legitimate)
    # NoSA=10, Tac=10, Tbac=5, Tup=10, NUFP=10
    # ABM = (10/10) * (10/5) * (10/10) = 2.0 (Note: Formula allows > 1.0 depending on density)
    # Wait, the paper formula (NoSA/Tac) * (NUFP/Tbac) * (Tup/Tac) 
    # if NUFP=10 and Tbac=5, Factor 2 is 2.0.
    for i in range(10):
        at.add_trace(TraceEntry("legit", f"b{i%5}", "update", "now", "success", True, True))
        
    # User 2: Malicious (Repeated failures, low compliance)
    # NoSA=2, Tac=10, Tbac=2, Tup=10, NUFP=1
    # ABM = (2/10) * (1/2) * (10/10) = 0.1
    for i in range(10):
        status = "success" if i < 2 else "fail"
        ok = True if i == 0 else False
        at.add_trace(TraceEntry("malicious", f"b{i%2}", "update", "now", status, ok, ok))

    # User 3: Suspicious (Moderate metrics)
    # NoSA=8, Tac=10, Tbac=5, Tup=10, NUFP=5
    # ABM = (8/10) * (5/5) * (10/10) = 0.8
    for i in range(10):
        status = "success" if i < 8 else "fail"
        ok = True if i < 5 else False
        at.add_trace(TraceEntry("suspicious", f"b{i%5}", "update", "now", status, ok, ok))

    return at

def test_legitimate_user_allowed(abm_controller, access_data):
    # ABM score > 0.8
    assert abm_controller.compute_abm(access_data, "legit") > 0.8
    assert abm_controller.check_access(access_data, "legit") is True

def test_malicious_user_denied(abm_controller, access_data):
    # ABM score < 0.8
    assert abm_controller.compute_abm(access_data, "malicious") < 0.8
    assert abm_controller.check_access(access_data, "malicious") is False

def test_suspicious_user_threshold(abm_controller, access_data):
    # ABM score exactly 0.8 (in our mocked data)
    assert abm_controller.compute_abm(access_data, "suspicious") == 0.8
    assert abm_controller.check_access(access_data, "suspicious") is True

def test_zero_access_edge_case(abm_controller):
    at = AccessTrace()
    assert abm_controller.compute_abm(at, "new_user") == 0.0
    assert abm_controller.check_access(at, "new_user") is False

def test_performance_calculation(abm_controller):
    true_labels = {"u1": "legitimate", "u2": "malicious"}
    # Correct prediction: u1 allowed, u2 denied
    predictions = {"u1": True, "u2": False}
    perf = abm_controller.get_access_restriction_performance(true_labels, predictions)
    assert perf == 100.0
    
    # 50% performance
    predictions = {"u1": False, "u2": False} # u1 misclassified
    perf = abm_controller.get_access_restriction_performance(true_labels, predictions)
    assert perf == 50.0
