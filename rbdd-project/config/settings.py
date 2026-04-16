"""Global configuration settings for the RBDD project."""

# Paper scale parameters
NUM_USERS = 500
NUM_DATA_FEATURES = 200
RANDOM_SEED = 42

# Thresholds
ABM_THRESHOLD = 0.8
BLRM_THRESHOLD = 0.6

# Evaluation ranges for Tables 2, 3, 4, 5
BLOCK_SIZES = [50, 100, 150, 200]      # For Tables 3, 4, 5
FEATURE_SIZES = [25, 50, 100, 200]     # For Table 2

# Encryption settings
SYSTEM_KEY_LENGTH = 256  # bits (AES-256)
SESSION_KEY_ROTATION = True
