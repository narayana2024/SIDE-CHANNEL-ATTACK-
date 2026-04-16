"""Tests for the evaluation metrics."""

import pytest
from src.evaluation.metrics import (
    compute_access_restriction,
    compute_deduplication_performance,
    compute_encryption_performance,
    compute_time_complexity,
    validate_against_published
)

def test_restriction_metric():
    # 97 malicious identified out of 100
    assert compute_access_restriction(97, 100) == 97.0
    # Boundary case: zero malicious
    assert compute_access_restriction(0, 0) == 100.0

def test_deduplication_metric():
    # 95 duplicates caught out of 100
    assert compute_deduplication_performance(95, 100) == 95.0

def test_encryption_metric():
    # 19 blocks secure out of 20
    assert compute_encryption_performance(19, 20) == 95.0

def test_time_metric():
    assert compute_time_complexity(10.0, 33.0) == 23.0
    assert compute_time_complexity(50.0, 40.0) == 0.0

def test_validation_logic():
    published = {"acc": 97.0, "dedup": 95.0}
    computed_good = {"acc": 97.2, "dedup": 94.8}
    computed_bad = {"acc": 90.0, "dedup": 95.0}
    
    assert validate_against_published(computed_good, published, tolerance=0.5) is True
    assert validate_against_published(computed_bad, published, tolerance=0.5) is False
