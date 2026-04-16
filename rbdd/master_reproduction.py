"""Master Reproduction Script for RBDD Research.

Executes the entire end-to-end pipeline:
1. Simulation & Validation
2. Multi-run Statistical Evaluation
3. Publication Figure Generation
"""

import os
import subprocess
import sys
from loguru import logger

def run_command(command, description):
    logger.info(f"STARTING: {description}...")
    # Set PYTHONPATH to current directory to ensure src/scripts imports work
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    try:
        subprocess.run(command, check=True, shell=True, env=env)
        logger.success(f"COMPLETED: {description}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FAILED: {description} (Exit code: {e.returncode})")
        sys.exit(1)

def main():
    logger.info("=== RBDD MASTER REPRODUCTION PIPELINE START ===")
    
    # 1. Base Simulation and Validation (Produces JSON/TeX/PNG Tables)
    run_command(
        "python scripts/run_simulation.py",
        "Base Simulation & Validation against Ground Truth"
    )

    # 2. Rigorous Statistical Analysis (10 runs, t-tests, CI)
    run_command(
        "python src/evaluation/evaluate_all.py --runs 10",
        "Multi-run Rigorous Statistical Evaluation"
    )

    # 3. Figure Generation
    run_command(
        "python scripts/generate_all_figures.py",
        "Publication-Quality Figure Generation"
    )

    logger.info("=== RBDD MASTER REPRODUCTION PIPELINE FINISHED ===")
    logger.info("All results are located in the 'reports/' directory.")
    print("\nNext steps: Review 'reports/results/statistical_analysis.txt' and 'reports/figures/' folder.")

if __name__ == "__main__":
    main()
