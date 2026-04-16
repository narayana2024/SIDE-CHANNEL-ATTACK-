"""Access Trace (ATr) data structure for tracking user behavioral metrics."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Set
from loguru import logger

@dataclass
class TraceEntry:
    """Represents a single user access trace."""
    user_id: str
    block_id: str
    access_type: str  # "read" or "update"
    timestamp: str    # ISO format string for JSON compatibility
    status: str       # "success" or "fail"
    format_ok: bool
    protocol_followed: bool

class AccessTrace:
    """Manages the collection of access traces and computes behavioral metrics."""

    def __init__(self):
        """Initializes an empty access trace collection."""
        self.traces: List[TraceEntry] = []
        logger.debug("Initialized empty Access Trace collection.")

    def add_trace(self, entry: TraceEntry):
        """Adds observation trace to collection."""
        self.traces.append(entry)

    def get_user_traces(self, user_id: str) -> List[TraceEntry]:
        """Eq. 1: UT_r - Returns all traces associated with a user."""
        return [t for t in self.traces if t.user_id == user_id]

    def get_total_access_count(self, user_id: str) -> int:
        """Eq. 2: Tac - Total number of access attempts by the user."""
        return len(self.get_user_traces(user_id))

    def get_distinct_blocks_accessed(self, user_id: str) -> int:
        """Eq. 3: Tbac - Total distinct blocks accessed by the user."""
        user_traces = self.get_user_traces(user_id)
        return len({t.block_id for t in user_traces})

    def get_total_updates(self, user_id: str) -> int:
        """Eq. 4: Tup - Total update operations performed by the user."""
        return sum(1 for t in self.get_user_traces(user_id) if t.access_type == "update")

    def get_protocol_compliant_updates(self, user_id: str) -> int:
        """Eq. 5: NUFP - Number of updates that adhered to protocol and format."""
        return sum(1 for t in self.get_user_traces(user_id) 
                  if t.access_type == "update" and t.format_ok and t.protocol_followed)

    def get_successful_accesses(self, user_id: str) -> int:
        """Eq. 6: NoSA - Number of successful access operations."""
        return sum(1 for t in self.get_user_traces(user_id) if t.status == "success")

    def load_from_json(self, filepath: str):
        """Loads trace data from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.traces = [TraceEntry(**d) for d in data]
            logger.info(f"Loaded {len(self.traces)} traces from {filepath}.")
        except Exception as e:
            logger.error(f"Failed to load access traces: {e}")

    def export_to_json(self, filepath: str):
        """Saves trace data to a JSON file."""
        data = [asdict(t) for t in self.traces]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(self.traces)} traces to {filepath}.")

    def __len__(self) -> int:
        return len(self.traces)
