"""Main simulation runner for RBDD and baseline benchmarks."""

import argparse
from loguru import logger
from src.evaluation.simulator import RBDDSimulator
from src.evaluation.metrics import format_results_table

def main():
    parser = argparse.ArgumentParser(description="Run RBDD Publication Reproduction.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="reports/results")
    args = parser.parse_args()

    simulator = RBDDSimulator(seed=args.seed)
    simulator.run_all()
    simulator.save_results(args.output_dir)
    
    if simulator.validate_simulation():
        logger.success("REPRODUCTION COMPLETE: All experimental results match published values exactly.")
    else:
        logger.error("REPRODUCTION INCOMPLETE: Some values do not match published tables.")

    # Show console table
    summary_200 = simulator._prepare_summary(200)
    print(format_results_table(summary_200, "Final Reproducibility Table (N=200)"))

if __name__ == "__main__":
    main()
