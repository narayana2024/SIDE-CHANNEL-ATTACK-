"""Tests for the MLE baseline."""

import pytest
from src.models.baselines.mle import MLEBaseline
from src.models.baselines.mpt import MPTBaseline
from src.models.baselines.sd2m import SD2MBaseline

@pytest.fixture
def mle():
    return MLEBaseline()

def test_mle_reproduction_values(mle):
    # Scale 200 features
    res = mle.run_simulation(200, mode="features")
    assert res["access_restriction"] == 76
    
    # Scale 200 blocks
    res = mle.run_simulation(200, mode="blocks")
    assert res["deduplication"] == 71
    assert res["encryption"] == 72
    assert res["time_complexity"] == 62

def test_mle_encryption(mle):
    data = b"testdata"
    key = b"12345678901234567890123456789012"
    cipher = mle.encrypt(data, key)
    assert cipher != data
    # MLE is deterministic
    assert mle.encrypt(data, key) == cipher

def test_mle_deduplication(mle):
    blocks = [b"a", b"a", b"b"]
    res = mle.deduplicate(blocks, set())
    assert res["duplicate"] == 1
    assert res["unique"] == 2

@pytest.fixture
def mpt():
    return MPTBaseline()

def test_mpt_reproduction_values(mpt):
    # Scale 200 features
    res = mpt.run_simulation(200, mode="features")
    assert res["access_restriction"] == 82
    
    # Scale 200 blocks
    res = mpt.run_simulation(200, mode="blocks")
    assert res["deduplication"] == 76
    assert res["encryption"] == 78
    assert res["time_complexity"] == 58

def test_mpt_mapping(mpt):
    data = b"block1"
    mpt.map_data(data, "userA")
    res = mpt.deduplicate_with_mapping([data], "userB")
    assert res["duplicate"] == 1
    assert "userB" in mpt.master_mapping[hashlib.sha256(data).hexdigest()]

@pytest.fixture
def sd2m():
    return SD2MBaseline()

def test_sd2m_reproduction_values(sd2m):
    # Scale 200 features
    res = sd2m.run_simulation(200, mode="features")
    assert res["access_restriction"] == 85
    
    # Scale 200 blocks
    res = sd2m.run_simulation(200, mode="blocks")
    assert res["deduplication"] == 81
    assert res["encryption"] == 83
    assert res["time_complexity"] == 52

def test_sd2m_blocking(sd2m):
    data = b"x" * 2048
    blocks = sd2m.smart_block(data, block_size=1024)
    assert len(blocks) == 2

import hashlib
