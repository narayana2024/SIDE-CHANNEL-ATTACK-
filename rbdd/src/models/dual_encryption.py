"""Dual-Mode Data Encryption/Decryption implementation for RBDD.

This module provides two layers of encryption:
1. System-level (Cloud session key rotation).
2. User-level (User-specific secret key).
"""

import os
import time
from typing import List, Tuple
from loguru import logger
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class DualModeEncryption:
    """Implements Equation 14 through Equation 17 from the RBDD paper."""

    def __init__(self, key_length: int = 32):  # 32 bytes = 256 bits
        self.key_length = key_length
        # For simulation, we use a fixed IV to allow predictable (but multi-layered) 
        # ciphertexts within the same session/key context.
        self.iv = b'\x00' * 16 
        logger.info(f"Dual-Mode Encryption initialized with {key_length*8}-bit key length.")

    def generate_system_key(self) -> bytes:
        """Generates a new random system key for a session."""
        return get_random_bytes(self.key_length)

    def rotate_session_key(self, block_id: str) -> bytes:
        """Equation 15: Dynamic key generation/rotation per session.
        
        Note: The decision logic to reuse vs rotate is handled by the PageMatrix/Orchestrator.
        This provides the mechanism to produce the new key.
        """
        new_key = self.generate_system_key()
        logger.debug(f"Rotated system key for block {block_id}.")
        return new_key

    def _aes_encrypt(self, data: bytes, key: bytes) -> bytes:
        """AES-256-CBC internal encryption."""
        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(data, AES.block_size))

    def _aes_decrypt(self, cipher_data: bytes, key: bytes) -> bytes:
        """AES-256-CBC internal decryption."""
        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return unpad(cipher.decrypt(cipher_data), AES.block_size)

    def system_encrypt(self, block: bytes, system_key: bytes) -> bytes:
        """Equation 14: System-level encryption of block."""
        return self._aes_encrypt(block, system_key)

    def system_decrypt(self, cipher: bytes, system_key: bytes) -> bytes:
        """Inverse of Equation 14."""
        return self._aes_decrypt(cipher, system_key)

    def user_encrypt(self, block: bytes, user_key: bytes) -> bytes:
        """Equation 16: User-level encryption with user key."""
        return self._aes_encrypt(block, user_key)

    def user_decrypt(self, cipher: bytes, user_key: bytes) -> bytes:
        """Inverse of Equation 16."""
        return self._aes_decrypt(cipher, user_key)

    def dual_encrypt(self, block: bytes, system_key: bytes, user_key: bytes) -> bytes:
        """Performs two-layer encryption.
        
        Flow: Data -> User Encryption -> System Encryption
        (System is the outer layer as per Equation 14's typical position in cloud cycles)
        """
        # Step 1: User Level (MLE-like or Secret)
        user_enc = self.user_encrypt(block, user_key)
        # Step 2: System Level (Session-rotating)
        system_enc = self.system_encrypt(user_enc, system_key)
        
        logger.debug("Performed Dual-Mode Encryption (User -> System).")
        return system_enc

    def dual_decrypt(self, cipher: bytes, system_key: bytes, user_key: bytes) -> bytes:
        """Performs two-layer decryption.
        
        Flow: Cipher -> System Decryption -> User Decryption
        """
        # Step 1: System Level (Outer layer)
        system_dec = self.system_decrypt(cipher, system_key)
        # Step 2: User Level (Inner layer)
        user_dec = self.user_decrypt(system_dec, user_key)
        
        logger.debug("Performed Dual-Mode Decryption (System -> User).")
        return user_dec

    def get_encryption_performance(self, test_blocks: List[bytes]) -> float:
        """Measures encryption/decryption success rate.
        
        Aiming for the 95% target at 200 blocks.
        """
        success_count = 0
        total = len(test_blocks)
        
        if total == 0:
            return 0.0

        for block in test_blocks:
            sk = self.generate_system_key()
            uk = self.generate_system_key()
            
            try:
                cipher = self.dual_encrypt(block, sk, uk)
                plain = self.dual_decrypt(cipher, sk, uk)
                if plain == block:
                    success_count += 1
            except Exception as e:
                logger.error(f"Encryption performance failure: {e}")
                
        performance = (success_count / total) * 100
        logger.info(f"Encryption/Decryption Performance: {performance:.2f}%")
        return performance
