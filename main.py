"""Main entry point for running the RBDD project simulations."""
import argparse
import sys
from loguru import logger

from src.utils.logger import setup_logger
from src.config import config

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="RBDD vs Baselines (MLE, MPT, SD2M) Simulation."
    )
    parser.add_argument(
        "--users",
        type=int,
        default=config.num_users,
        help=f"Number of users (default: {config.num_users})"
    )
    parser.add_argument(
        "--features",
        type=int,
        default=config.num_data_features,
        help=f"Number of data features (default: {config.num_data_features})"
    )
    parser.add_argument(
        "--blocks",
        type=int,
        default=config.num_blocks,
        help=f"Number of blocks (default: {config.num_blocks})"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    return parser.parse_args()

def main() -> None:
    """Main execution function."""
    args = parse_arguments()
    setup_logger(args.log_level)
    
    logger.info("Starting RBDD Simulation Environment...")
    logger.info(f"Parameters: {args.users} Users, {args.features} Features, {args.blocks} Blocks")
    
    # TODO: Implement phases:
    # 1. Initialize environments and synthetic data.
    # 2. Run Access Restriction Phase (ABM vs Baselines)
    # 3. Run Deduplication Phase (BLRM vs Baselines)
    # 4. Run Encryption Phase (Dual-Mode vs Baselines)
    # 5. Measure Time Complexity
    # 6. Generate comparative plots and save results to CSV.

    logger.info("Simulation completed successfully.")

if __name__ == "__main__":
    main()
