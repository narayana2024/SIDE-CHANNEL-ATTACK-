"""RBDD Framework Orchestrator - Integrating ABM, BLRM, and Dual-Mode Encryption.

This module implements the unified logic for secure cloud deduplication as
described in the RBDD research paper.
"""

import time
from typing import List, Dict, Any, Tuple
from loguru import logger
from src.models.abm import ABMAccessControl
from src.models.blrm import BLRMDeduplication
from src.models.dual_encryption import DualModeEncryption
from src.data.page_matrix import PageMatrix, PageMatrixEntry
from src.data.access_traces import AccessTrace

class RBDDFramework:
    """Main orchestrator for the Real-Time Block-Level Dual-Mode Data Deduplication."""

    def __init__(self, abm_threshold: float = 0.8, blrm_threshold: float = 0.6, 
                 key_length_bits: int = 256, block_size: int = 1024):
        """Initializes all framework components.
        
        Args:
            abm_threshold: Access Restriction threshold (default 0.8).
            blrm_threshold: Deduplication threshold (default 0.6).
            key_length_bits: Encryption key length (default 256 bits).
            block_size: Size of blocks for BLRM (default 1024 bytes).
        """
        self.abm = ABMAccessControl(threshold=abm_threshold)
        self.blrm = BLRMDeduplication(threshold=blrm_threshold, block_size=block_size)
        self.crypto = DualModeEncryption(key_length=key_length_bits // 8)
        self.block_size = block_size
        
        logger.info("RBDD Framework components initialized.")

    def process_request(self, user_id: str, data: bytes, request_type: str, 
                        access_traces: AccessTrace, page_matrix: PageMatrix,
                        user_key: bytes) -> Dict[str, Any]:
        """Processes a single data upload/update request through the complete RBDD pipeline.
        
        Algorithm Steps:
        1. Access Restriction (ABM) check.
        2. Block segmentation.
        3. Block-Level Deduplication (BLRM).
        4. Dual-Mode Encryption.
        5. Page Matrix update.
        """
        start_time = time.time()
        
        # 1. Access Restriction Phase
        is_allowed = self.abm.check_access(access_traces, user_id)
        if not is_allowed:
            logger.warning(f"Request from user {user_id} REJECTED by ABM.")
            return {
                "status": "REJECTED",
                "reason": "ABM_THRESHOLD_NOT_MET",
                "time_taken": time.time() - start_time
            }

        logger.info(f"Processing {request_type} request for user {user_id}...")
        
        # 2. Split Data into Blocks (Eq 9)
        blocks_data = self.blrm.split_data_to_blocks(data)
        
        processed_stats = {
            "total_blocks": len(blocks_data),
            "duplicates": 0,
            "unique": 0,
            "saved_bytes": 0
        }

        # 3-5. Process each block
        for i, block in enumerate(blocks_data):
            # Compute BLRM (Eq 10-12)
            blrm_score = self.blrm.compute_blrm(block, page_matrix)
            
            if blrm_score >= self.blrm.threshold:
                # Deduplication Decision: DUPLICATE (Eq 13)
                processed_stats["duplicates"] += 1
                processed_stats["saved_bytes"] += len(block)
                logger.debug(f"Block {i} identified as DUPLICATE. Skipping storage.")
            else:
                # Deduplication Decision: UNIQUE (Eq 13)
                processed_stats["unique"] += 1
                
                # Dual-Mode Encryption
                # Generate new system key if it's a new unique block (Eq 15)
                block_id = f"blk_{user_id}_{int(time.time()*1000)}_{i}"
                sys_key = self.crypto.generate_system_key()
                
                cipher = self.crypto.dual_encrypt(block, sys_key, user_key)
                
                # Update Page Matrix
                page_matrix.add_entry(
                    block_id=block_id,
                    content=block,
                    user_key=user_key.hex(),
                    system_key=sys_key.hex(),
                    scheme="AES-256-CBC",
                    user_id=user_id
                )
                # Store extra metadata needed for PBS similarity (optional high fidelity)
                entry = page_matrix.get_entry(block_id)
                if entry:
                    entry.metadata["content_hex"] = block.hex()

        processed_stats["status"] = "COMPLETED"
        processed_stats["time_taken"] = time.time() - start_time
        
        logger.info(
            f"Request completed. Summary: {processed_stats['duplicates']} Duplicates removed, "
            f"{processed_stats['unique']} Unique blocks stored."
        )
        return processed_stats

    def measure_time_complexity(self, num_blocks: int, user_id: str = "test_user") -> float:
        """Measures processing time for a given number of blocks.
        
        Aiming for the 23s target at 200 blocks.
        """
        # Create dummy trace data to satisfy ABM
        at = AccessTrace()
        from src.data.access_traces import TraceEntry
        for _ in range(10):
            at.add_trace(TraceEntry(user_id, "b1", "read", "now", "success", True, True))
            
        pm = PageMatrix()
        # Create dummy data of size (num_blocks * 1024)
        data = b"X" * (num_blocks * self.block_size)
        ukey = b"U" * 32
        
        start_time = time.time()
        self.process_request(user_id, data, "upload", at, pm, ukey)
        elapsed = time.time() - start_time
        
        logger.info(f"Time Complexity for {num_blocks} blocks: {elapsed:.2f} seconds.")
        return elapsed

    def run_simulation(self, users_data: List[Dict], blocks_data: List[bytes], 
                      access_traces: AccessTrace) -> Dict[str, float]:
        """Runs the complete end-to-end simulation to reproduce paper metrics.
        
        Args:
            users_data: List of user profiles (with 'type' and 'user_id').
            blocks_data: List of raw blocks to process.
            access_traces: The trace dataset for ABM evaluation.
            
        Returns:
            Dict: Final metrics (restriction_acc, deduplication_rate, encryption_succ).
        """
        logger.info("Starting Full RBDD Simulation...")
        pm = PageMatrix()
        
        # 1. Evaluate Access Restriction
        predictions = {}
        true_labels = {u["user_id"]: u["type"] for u in users_data}
        
        for user in users_data:
            predictions[user["user_id"]] = self.abm.check_access(access_traces, user["user_id"])
            
        restriction_acc = self.abm.get_access_restriction_performance(true_labels, predictions)

        # 2. Evaluate Deduplication & Encryption
        # We process unique data blocks from 'legitimate' users only (restricted access)
        legit_users = [u for u in users_data if predictions[u["user_id"]]]
        if not legit_users:
            logger.error("No users allowed by ABM. Cannot evaluate deduplication.")
            return {"restriction": restriction_acc, "deduplication": 0, "encryption": 0}

        # To simulate deduplication reliably, we pass a stream of blocks through process_request
        # We use a subset for measuring rate
        sample_size = min(len(blocks_data), 200)
        data_to_store = b"".join(blocks_data[:sample_size])
        
        user = legit_users[0]
        ukey = b"U" * 32
        
        results = self.process_request(user["user_id"], data_to_store, "upload", access_traces, pm, ukey)
        
        dedup_rate = 0
        if results["total_blocks"] > 0:
            dedup_rate = (results["duplicates"] / results["total_blocks"]) * 100
            
        # 3. Encryption Success (verified by roundtrip in processing or separate method)
        enc_succ = self.crypto.get_encryption_performance(blocks_data[:sample_size])

        final_metrics = {
            "restriction": restriction_acc,
            "deduplication": dedup_rate,
            "encryption": enc_succ
        }
        
        logger.info(f"Simulation Final Metrics: {final_metrics}")
        return final_metrics
