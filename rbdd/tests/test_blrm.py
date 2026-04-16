"""Tests for the Block-Level Relational Measure (BLRM) deduplication logic."""

import pytest
from src.models.blrm import BLRMDeduplication
from src.data.page_matrix import PageMatrix

@pytest.fixture
def blrm_handler():
    return BLRMDeduplication(threshold=0.6, block_size=10)

@pytest.fixture
def populated_pm():
    pm = PageMatrix()
    # Adding a base block
    content = b"ABCDEFGHIJ" 
    pm.add_entry("b1", content, "k", "s", "AES", "u1")
    # Store content in metadata for PBS simulation
    pm.get_entry("b1").metadata["content_hex"] = content.hex()
    return pm

def test_split_data(blrm_handler):
    data = b"0123456789ABCDEFGHIJ"
    blocks = blrm_handler.split_data_to_blocks(data)
    assert len(blocks) == 2
    assert blocks[0] == b"0123456789"
    assert blocks[1] == b"ABCDEFGHIJ"

def test_exact_duplicate_detection(blrm_handler, populated_pm):
    # Same as b1
    dup_block = b"ABCDEFGHIJ"
    score = blrm_handler.compute_blrm(dup_block, populated_pm)
    assert score >= 0.6  # Decision: DUPLICATE
    
    results = blrm_handler.evaluate_deduplication([dup_block], populated_pm)
    assert results["duplicate"] == 1

def test_unique_block_detection(blrm_handler, populated_pm):
    # Completely different
    unique_block = b"0123456789"
    score = blrm_handler.compute_blrm(unique_block, populated_pm)
    assert score < 0.6  # Decision: UNIQUE
    
    results = blrm_handler.evaluate_deduplication([unique_block], populated_pm)
    assert results["unique"] == 1

def test_partial_duplicate_logic(blrm_handler, populated_pm):
    # 80% similar (8 bytes match: ABCDEFGHXX)
    partial_block = b"ABCDEFGHXX"
    # CBS for this will be 0.0 in literal Eq 10. 
    # Current implementation handles CBS=1 if match exists, 0 otherwise.
    # To test PBS explicitly:
    cbs = blrm_handler.compute_cbs(partial_block, populated_pm)
    pbs = blrm_handler.compute_pbs(partial_block, populated_pm)
    
    assert cbs == 0.0 # No exact match
    assert pbs > 0.0  # Should find partial match in PM
    
def test_performance_metric(blrm_handler):
    perf = blrm_handler.get_deduplication_performance(100, 95)
    assert perf == 95.0
