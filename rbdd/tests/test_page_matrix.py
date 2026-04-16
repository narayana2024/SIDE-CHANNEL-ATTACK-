"""Tests for the PageMatrix data structure."""

import pytest
import os
import tempfile
from src.data.page_matrix import PageMatrix, PageMatrixEntry

def test_add_and_get_entry():
    pm = PageMatrix()
    content = b"test content"
    pm.add_entry("block1", content, "user_key_1", "sys_key_A", "AES", "user1")
    
    assert len(pm) == 1
    entry = pm.get_entry("block1")
    assert entry is not None
    assert entry.block_id == "block1"
    assert entry.user_id == "user1"
    assert entry.system_key == "sys_key_A"

def test_system_key_rotation():
    pm = PageMatrix()
    pm.add_entry("block1", b"data", "ukey", "skey1", "AES", "u1")
    
    pm.update_system_key("block1", "skey2")
    entry = pm.get_entry("block1")
    assert entry.system_key == "skey2"

def test_duplicate_check():
    pm = PageMatrix()
    pm.add_entry("block1", b"data", "ukey", "skey1", "AES", "u1")
    # Adding same ID should return False (update instead of override)
    result = pm.add_entry("block1", b"data", "ukey", "skey1", "AES", "u1")
    assert result is False
    assert len(pm) == 1

def test_remove_duplicate():
    pm = PageMatrix()
    pm.add_entry("block1", b"data", "ukey", "skey1", "AES", "u1")
    pm.remove_duplicate("block1")
    assert len(pm) == 0

def test_decryption_permit():
    pm = PageMatrix()
    pm.add_entry("block1", b"data", "user_k", "sys_k", "AES", "u1")
    
    # Correct keys
    assert pm.get_decrypted_content("block1", "sys_k", "user_k") == "DECRYPTION_PERMITTED"
    
    # Incorrect system key
    with pytest.raises(ValueError, match="Invalid System Key"):
        pm.get_decrypted_content("block1", "wrong_sys", "user_k")
        
    # Incorrect user key
    with pytest.raises(ValueError, match="Invalid User Key"):
        pm.get_decrypted_content("block1", "sys_k", "wrong_user")

def test_json_io():
    pm = PageMatrix()
    pm.add_entry("block1", b"data", "ukey", "skey1", "AES", "u1")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        
    try:
        pm.export_to_json(tmp_path)
        
        pm2 = PageMatrix()
        pm2.import_from_json(tmp_path)
        
        assert len(pm2) == 1
        assert pm2.get_entry("block1").block_id == "block1"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
