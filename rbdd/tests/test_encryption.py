"""Tests for the Dual-Mode Encryption/Decryption logic."""

import pytest
from src.models.dual_encryption import DualModeEncryption

@pytest.fixture
def encryptor():
    return DualModeEncryption(key_length=32)

def test_encryption_roundtrip(encryptor):
    data = b"Sensitive research data for RBDD project."
    sk = encryptor.generate_system_key()
    uk = encryptor.generate_system_key()
    
    cipher = encryptor.dual_encrypt(data, sk, uk)
    assert cipher != data
    
    plain = encryptor.dual_decrypt(cipher, sk, uk)
    assert plain == data

def test_system_key_impact(encryptor):
    data = b"Identical block data"
    sk1 = encryptor.generate_system_key()
    sk2 = encryptor.generate_system_key()
    uk = encryptor.generate_system_key()
    
    # Same data, same user key, but different system keys (different sessions/users)
    cipher1 = encryptor.dual_encrypt(data, sk1, uk)
    cipher2 = encryptor.dual_encrypt(data, sk2, uk)
    
    # They should be distinct to prevent cross-user inference
    assert cipher1 != cipher2

def test_session_key_rotation(encryptor):
    data = b"Block content"
    block_id = "block_101"
    uk = encryptor.generate_system_key()
    
    sk_old = encryptor.generate_system_key()
    c1 = encryptor.dual_encrypt(data, sk_old, uk)
    
    sk_new = encryptor.rotate_session_key(block_id)
    c2 = encryptor.dual_encrypt(data, sk_new, uk)
    
    assert sk_old != sk_new
    assert c1 != c2

def test_performance_measurement(encryptor):
    blocks = [b"data1", b"data2", b"data3"] * 10
    perf = encryptor.get_encryption_performance(blocks)
    assert perf == 100.0
