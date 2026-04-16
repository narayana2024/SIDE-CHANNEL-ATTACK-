"""Configuration parameters for the RBDD simulation and baselines."""
import dataclasses

@dataclasses.dataclass
class SimulationConfig:
    """Configuration parameters matching the published simulation setup."""
    num_users: int = 500
    num_data_features: int = 200
    num_blocks: int = 200
    
    # RBDD specific thresholds
    abm_threshold: float = 0.8
    blrm_threshold: float = 0.6
    
    # Target values to aim for in reproduction (for sanity checking results)
    # Access Restriction (200 features): RBDD 97%, MLE 76%, MPT 82%, SD2M 85%
    # Deduplication (200 blocks): RBDD 95%, MLE 71%, MPT 76%, SD2M 81%
    # Encryption/Decryption (200 blocks): RBDD 95%, MLE 72%, MPT 78%, SD2M 83%
    # Time Complexity (200 blocks): RBDD 23s, MLE 62s, MPT 58s, SD2M 52s

config = SimulationConfig()
