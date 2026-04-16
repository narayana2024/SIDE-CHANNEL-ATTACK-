"""Access Behavioral Measure (ABM) for user access restriction.

ABM implements a three-component behavioral analysis to identify and 
mitigate side-channel attacks by monitoring user interaction patterns.
"""

import numpy as np
from typing import Dict, List, Any
from loguru import logger
from src.data.access_traces import AccessTrace

class ABMAccessControl:
    """Implements Equation 1 through Equation 8 from the RBDD paper."""

    def __init__(self, threshold: float = 0.8):
        """Initializes the ABM controller with a security threshold.
        
        Args:
            threshold: The ABM value required to allow access (default 0.8).
        """
        self.threshold = threshold
        logger.info(f"ABM initialized with threshold: {self.threshold}")

    def compute_abm(self, access_traces: AccessTrace, user_id: str) -> float:
        """Calculates the composite ABM score using Equation 7.
        
        Equation 7: ABM = (NoSA/Tac) * (NUFP/Tbac) * (Tup/Tac)
        
        Args:
            access_traces: The history of all traced accesses.
            user_id: The ID of the user to evaluate.
            
        Returns:
            float: The calculated ABM score (0.0 to 1.0).
        """
        tac = access_traces.get_total_access_count(user_id)
        if tac == 0:
            logger.debug(f"User {user_id} has zero accesses. ABM = 0.0")
            return 0.0

        nosa = access_traces.get_successful_accesses(user_id)
        tbac = access_traces.get_distinct_blocks_accessed(user_id)
        tup = access_traces.get_total_updates(user_id)
        nufp = access_traces.get_protocol_compliant_updates(user_id)

        # Factor 1: Success Rate (NoSA / Tac)
        success_ratio = nosa / tac
        
        # Factor 2: Protocol Compliance Density (NUFP / Tbac)
        # Note: If Tbac is 0 (though unlikely if Tac > 0), set ratio to 0
        protocol_ratio = nufp / tbac if tbac > 0 else 0.0
        
        # Factor 3: Update Intensity (Tup / Tac)
        update_ratio = tup / tac

        abm_score = success_ratio * protocol_ratio * update_ratio
        
        logger.debug(
            f"User {user_id} Metrics - Tac:{tac}, NoSA:{nosa}, Tbac:{tbac}, "
            f"Tup:{tup}, NUFP:{nufp} | ABM Score: {abm_score:.4f}"
        )
        return abm_score

    def check_access(self, access_traces: AccessTrace, user_id: str) -> bool:
        """Determines if access should be ALLOWED or DENIED (Equation 8).
        
        Args:
            access_traces: The trace dataset.
            user_id: The user to verify.
            
        Returns:
            bool: True (ALLOW) or False (DENY).
        """
        abm = self.compute_abm(access_traces, user_id)
        
        if abm >= self.threshold:
            logger.success(f"Access ALLOWED for user {user_id} (ABM: {abm:.4f})")
            return True
        else:
            logger.warning(
                f"Access DENIED for user {user_id} (ABM: {abm:.4f} < {self.threshold}). "
                "Possible Side-Channel Attack or anomalous pattern detected."
            )
            return False

    def evaluate_all_users(self, access_traces: AccessTrace, user_ids: List[str]) -> Dict[str, Any]:
        """Performs batch evaluation for simulation results.
        
        Returns:
            Dict: Summary results (allow_count, deny_count, scores).
        """
        results = {"allow": 0, "deny": 0, "scores": {}}
        
        for uid in user_ids:
            score = self.compute_abm(access_traces, uid)
            results["scores"][uid] = score
            if score >= self.threshold:
                results["allow"] += 1
            else:
                results["deny"] += 1
                
        logger.info(
            f"Batch Evaluation: {results['allow']} Allowed, {results['deny']} Denied."
        )
        return results

    def get_access_restriction_performance(self, true_labels: Dict[str, str], 
                                           predictions: Dict[str, bool]) -> float:
        """Computes the access restriction % (accuracy of detection).
        
        Args:
            true_labels: Map of user_id to 'legitimate'/'malicious'.
            predictions: Map of user_id to ALLOW (True) / DENY (False).
            
        Returns:
            float: Restriction performance percentage (0.0 to 100.0).
        """
        correct = 0
        total = len(true_labels)
        
        if total == 0:
            return 0.0

        for uid, label in true_labels.items():
            is_allowed = predictions.get(uid, False)
            
            # Correct if legitimate user is Allowed OR malicious user is Denied
            if (label == 'legitimate' and is_allowed) or (label != 'legitimate' and not is_allowed):
                correct += 1
            else:
                logger.trace(f"Restriction Misclassification: User {uid} ({label}) was {is_allowed}")
                
        accuracy = (correct / total) * 100
        logger.info(f"Access Restriction Performance: {accuracy:.2f}%")
        return accuracy
