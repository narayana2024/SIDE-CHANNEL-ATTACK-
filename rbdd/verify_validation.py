from config.published_results import validate_results, TABLE_2_ACCESS_RESTRICTION
from loguru import logger

# Test successful validation
logger.info("Testing successful validation...")
success = validate_results(TABLE_2_ACCESS_RESTRICTION, "access_restriction")

# Test failed validation
logger.info("Testing failed validation...")
mismatched_data = TABLE_2_ACCESS_RESTRICTION.copy()
mismatched_data["RBDD"] = [0, 0, 0, 0]
failure = validate_results(mismatched_data, "access_restriction")

if success and not failure:
    print("\nValidation logic verified successfully!")
else:
    print("\nValidation logic verification failed.")
