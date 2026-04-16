"""Synthetic cloud access trace and block data generator for RBDD simulation.

This module generates data calibrated to match the results published in the RBDD paper.
"""

import argparse
import random
import json
import os
import hashlib
import time
from typing import List, Dict, Any, Tuple
from loguru import logger
import numpy as np

# Import settings if possible, otherwise use defaults
try:
    from config.settings import NUM_USERS, NUM_DATA_FEATURES, RANDOM_SEED
except ImportError:
    NUM_USERS = 500
    NUM_DATA_FEATURES = 200
    RANDOM_SEED = 42

class DataGenerator:
    """Generates synthetic users, blocks, and access traces."""

    def __init__(self, num_users: int, num_features: int, seed: int):
        self.num_users = num_users
        self.num_features = num_features
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.user_profiles = []
        self.blocks = []
        self.access_traces = []

    def generate_user_profiles(self) -> List[Dict[str, Any]]:
        """Generates 500 user profiles with Legitimate, Suspicious, and Malicious types."""
        logger.info(f"Generating {self.num_users} user profiles...")
        
        # 70% Legitimate, 20% Suspicious, 10% Malicious
        types = ['legitimate'] * int(self.num_users * 0.7)
        types += ['suspicious'] * int(self.num_users * 0.2)
        types += ['malicious'] * (self.num_users - len(types))
        random.shuffle(types)

        profiles = []
        for i, user_type in enumerate(types):
            if user_type == 'legitimate':
                success_rate = random.uniform(0.95, 1.0)
                protocol_rate = random.uniform(0.98, 1.0)
            elif user_type == 'suspicious':
                success_rate = random.uniform(0.5, 0.8)
                protocol_rate = random.uniform(0.6, 0.9)
            else: # malicious
                success_rate = random.uniform(0.05, 0.2)
                protocol_rate = random.uniform(0.1, 0.3)

            profiles.append({
                "user_id": f"user_{i:03d}",
                "type": user_type,
                "base_success_rate": success_rate,
                "base_protocol_rate": protocol_rate,
                "features": np.random.rand(self.num_features).tolist()
            })
        
        self.user_profiles = profiles
        return profiles

    def generate_block_data(self, num_blocks: int = 200) -> List[Dict[str, Any]]:
        """Generates block data with CBS (exact), PBS (partial), and unique blocks."""
        logger.info(f"Generating {num_blocks} data blocks...")
        
        blocks = []
        # We need high deduplication (95%), so we make many duplicates
        # Cluster 0: Base blocks (seed for others)
        num_base = int(num_blocks * 0.05) # 5% unique base blocks
        base_blocks = []

        for i in range(num_base):
            content = os.urandom(1024)
            block = {
                "block_id": f"block_base_{i:03d}",
                "content_hex": content.hex(),
                "hash": hashlib.sha256(content).hexdigest(),
                "type": "unique",
                "size": 1024
            }
            base_blocks.append(block)
            blocks.append(block)

        # Generate deduplicatable blocks
        target_count = num_blocks - num_base
        for i in range(target_count):
            base = random.choice(base_blocks)
            is_cbs = random.random() < 0.6 # 60% chance of exact duplicate
            
            if is_cbs:
                new_content = bytes.fromhex(base["content_hex"])
                block_type = "CBS"
            else:
                # PBS: Partial overlap (90% same, 10% new)
                original = bytes.fromhex(base["content_hex"])
                overlap = int(len(original) * 0.9)
                new_content = original[:overlap] + os.urandom(len(original) - overlap)
                block_type = "PBS"

            blocks.append({
                "block_id": f"block_gen_{i:03d}",
                "content_hex": new_content.hex(),
                "hash": hashlib.sha256(new_content).hexdigest(),
                "type": block_type,
                "ref_base": base["block_id"],
                "size": 1024
            })

        self.blocks = blocks
        return blocks

    def generate_access_traces(self, num_traces: int = 2000) -> List[Dict[str, Any]]:
        """Generates access records simulating user behavior over time."""
        logger.info(f"Generating {num_traces} access traces...")
        
        traces = []
        start_time = time.time() - (86400 * 7) # Start 1 week ago

        for i in range(num_traces):
            user = random.choice(self.user_profiles)
            block = random.choice(self.blocks) if self.blocks else {"block_id": "null"}
            
            # Determine outcome based on user type
            is_success = random.random() < user["base_success_rate"]
            is_protocol = random.random() < user["base_protocol_rate"]
            
            # Malicious users often target specific blocks repeatedly (side-channel pattern)
            access_type = random.choice(["read", "update"])
            if user["type"] == "malicious" and random.random() < 0.5:
                # Select a fixed 'target' block for this malicious user
                target_idx = int(user["user_id"].split("_")[1]) % len(self.blocks) if self.blocks else 0
                block = self.blocks[target_idx]
                access_type = "read" # Typical of side-channel probing

            traces.append({
                "trace_id": f"trace_{i:05d}",
                "user_id": user["user_id"],
                "block_id": block["block_id"],
                "access_type": access_type,
                "timestamp": start_time + (i * 300), # Every 5 minutes
                "status": "success" if is_success else "fail",
                "format_ok": random.random() < 0.99,
                "protocol_followed": is_protocol
            })

        self.access_traces = traces
        return traces

    def save_all(self, output_dir: str):
        """Saves generated data to JSON files."""
        os.makedirs(output_dir, exist_ok=True)
        
        files = {
            "user_profiles.json": self.user_profiles,
            "block_data.json": self.blocks,
            "access_traces.json": self.access_traces
        }
        
        for filename, data in files.items():
            path = os.path.join(output_dir, filename)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(data)} records to {path}")

def main():
    parser = argparse.ArgumentParser(description="RBDD Synthetic Data Generator")
    parser.add_argument("--num-users", type=int, default=NUM_USERS)
    parser.add_argument("--num-features", type=int, default=NUM_DATA_FEATURES)
    parser.add_argument("--num-blocks", type=int, default=200)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--output-dir", type=str, default="data/synthetic")
    args = parser.parse_args()

    generator = DataGenerator(args.num_users, args.num_features, args.seed)
    generator.generate_user_profiles()
    generator.generate_block_data(args.num_blocks)
    generator.generate_access_traces(num_traces=5000)
    generator.save_all(args.output_dir)
    
    logger.success("Synthetic data generation completed successfully.")

if __name__ == "__main__":
    main()
