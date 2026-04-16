"""Page Matrix (PM) data structure for RBDD block metadata management."""

import json
import time
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional
from loguru import logger

@dataclass
class PageMatrixEntry:
    """Represents a single entry in the Page Matrix."""
    block_id: str
    encryption_key: str  # User's MLE/convergent key
    encryption_scheme: str  # e.g., 'AES-256-GCM'
    system_key: str  # Rotating session key
    content_hash: str
    user_id: str
    last_access: float = field(default_factory=time.time)
    access_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

class PageMatrix:
    """Manages the schema of data blocks in the cloud storage system."""

    def __init__(self):
        """Initializes an empty Page Matrix."""
        self.matrix: Dict[str, PageMatrixEntry] = {}
        logger.debug("Initialized empty Page Matrix.")

    def add_entry(self, block_id: str, content: bytes, user_key: str, 
                  system_key: str, scheme: str, user_id: str) -> bool:
        """Adds a new block entry to the matrix.
        
        Args:
            block_id: Unique identifier for the block.
            content: Raw or encrypted content to generate hash.
            user_key: The user-specific encryption key.
            system_key: The current session system key.
            scheme: Encryption method used.
            user_id: Owner of the block.
            
        Returns:
            bool: True if added successfully.
        """
        if block_id in self.matrix:
            logger.warning(f"Block {block_id} already exists. Updating existing entry.")
            self.matrix[block_id].access_count += 1
            self.matrix[block_id].last_access = time.time()
            return False

        content_hash = hashlib.sha256(content).hexdigest()
        
        entry = PageMatrixEntry(
            block_id=block_id,
            encryption_key=user_key,
            encryption_scheme=scheme,
            system_key=system_key,
            content_hash=content_hash,
            user_id=user_id
        )
        
        self.matrix[block_id] = entry
        logger.info(f"Added block {block_id} to Page Matrix for user {user_id}.")
        return True

    def get_entry(self, block_id: str) -> Optional[PageMatrixEntry]:
        """Retrieves block metadata.
        
        Args:
            block_id: Unique identifier.
            
        Returns:
            PageMatrixEntry or None if not found.
        """
        entry = self.matrix.get(block_id)
        if entry:
            entry.access_count += 1
            entry.last_access = time.time()
        return entry

    def update_system_key(self, block_id: str, new_key: str) -> bool:
        """Rotates the system key for a specific block.
        
        Args:
            block_id: Unique identifier.
            new_key: The new rotating session key.
            
        Returns:
            bool: True if updated.
        """
        if block_id in self.matrix:
            self.matrix[block_id].system_key = new_key
            self.matrix[block_id].last_access = time.time()
            logger.debug(f"Rotated system key for block {block_id}.")
            return True
        return False

    def get_all_blocks(self) -> List[PageMatrixEntry]:
        """Returns all entries for comparisons across the system."""
        return list(self.matrix.values())

    def get_decrypted_content(self, block_id: str, system_key: str, user_key: str) -> str:
        """Simulates the logic for two-stage decryption verification.
        
        Note: Actual cryptographic decryption happens in src.models.dual_encryption.
        This method serves as a flow validator.
        """
        entry = self.matrix.get(block_id)
        if not entry:
            raise ValueError(f"Block {block_id} not found.")
            
        if entry.system_key != system_key:
            raise ValueError("Invalid System Key: Session key rotation mismatch.")
            
        if entry.encryption_key != user_key:
            raise ValueError("Invalid User Key: Authorization failed.")
            
        return "DECRYPTION_PERMITTED"

    def remove_duplicate(self, block_id: str) -> bool:
        """Removes a duplicate block from the matrix.
        
        Args:
            block_id: Unique identifier.
            
        Returns:
            bool: True if removed.
        """
        if block_id in self.matrix:
            del self.matrix[block_id]
            logger.info(f"Removed duplicate block {block_id} from Page Matrix.")
            return True
        return False

    def export_to_json(self, filepath: str):
        """Serializes the matrix to a JSON file."""
        data = {bid: asdict(entry) for bid, entry in self.matrix.items()}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported Page Matrix to {filepath}.")

    def import_from_json(self, filepath: str):
        """Deserializes the matrix from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.matrix = {bid: PageMatrixEntry(**entry_data) for bid, entry_data in data.items()}
        logger.info(f"Imported {len(self.matrix)} entries from {filepath}.")

    def __len__(self) -> int:
        return len(self.matrix)
