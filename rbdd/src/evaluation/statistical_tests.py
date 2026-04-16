"""Advanced Statistical Testing module for RBDD evaluation.

Provides t-tests, bootstrap CI, Cohen's d effect size, and Bonferroni corrections.
"""

import json
import os
import numpy as np
from scipy import stats
from typing import List, Dict, Any
from loguru import logger

def calculate_cohens_d(x: List[float], y: List[float]) -> float:
    """Computes Cohen's d for paired samples."""
    diff = np.array(x) - np.array(y)
    if np.std(diff, ddof=1) == 0:
        return 0.0
    return np.mean(diff) / np.std(diff, ddof=1)

def bootstrap_ci(data: List[float], n_bootstrap: int = 1000, ci: float = 95) -> tuple:
    """Computes bootstrap confidence interval."""
    if len(set(data)) <= 1:
        return (data[0], data[0])
    
    means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))
    
    lower = (100 - ci) / 2
    upper = 100 - lower
    return tuple(np.percentile(means, [lower, upper]))

class StatisticalAnalyzer:
    """Performs rigorous statistical analysis on simulation results."""

    def __init__(self, simulation_results: List[Dict]):
        """
        Args:
            simulation_results: List of result dicts from independent runs.
        """
        self.runs = simulation_results
        self.metrics = ["access_restriction", "data_deduplication", "encryption_decryption", "time_complexity"]
        self.baselines = ["MLE", "MPT", "SD2M"]
        self.analysis = {}

    def perform_full_analysis(self, scale: int = 200) -> Dict[str, Any]:
        """Runs the entire statistical suite for all metrics/baselines."""
        logger.info(f"Performing statistical analysis for scale {scale}...")
        
        # Bonferroni correction factor
        m_tests = len(self.metrics) * len(self.baselines)
        alpha = 0.05
        corrected_alpha = alpha / m_tests
        
        full_report = {
            "alpha": alpha,
            "corrected_alpha": corrected_alpha,
            "results": {}
        }

        for metric in self.metrics:
            full_report["results"][metric] = {}
            # Collect RBDD values
            rbdd_vals = [r[metric][scale]["RBDD"] for r in self.runs]
            
            # 1. Capture RBDD baseline stats
            full_report["results"][metric]["RBDD"] = {
                "mean": float(np.mean(rbdd_vals)),
                "std": float(np.std(rbdd_vals)),
                "ci_95": bootstrap_ci(rbdd_vals)
            }

            # 2. Compare against each baseline
            for base in self.baselines:
                base_vals = [r[metric][scale][base] for r in self.runs]
                
                # Paired T-Test
                try:
                    t_stat, p_val = stats.ttest_rel(rbdd_vals, base_vals)
                except Exception:
                    t_stat, p_val = 0.0, 1.0

                # Cohen's d
                d = calculate_cohens_d(rbdd_vals, base_vals)
                
                # Significance decision
                is_significant = p_val < corrected_alpha if not np.isnan(p_val) else False

                full_report["results"][metric][base] = {
                    "mean": float(np.mean(base_vals)),
                    "std": float(np.std(base_vals)),
                    "ci_95": bootstrap_ci(base_vals),
                    "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                    "p_value": float(p_val) if not np.isnan(p_val) else 1.0,
                    "cohens_d": float(d),
                    "significant": bool(is_significant)
                }

        self.analysis = full_report
        return full_report

    def save_reports(self, output_path: str):
        """Saves analysis to JSON and creates a human-readable text summary."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 1. Save JSON
        json_path = output_path.replace(".txt", ".json")
        with open(json_path, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        
        # 2. Save Human Readable Summary
        with open(output_path, 'w') as f:
            f.write("=== RBDD RIGOROUS STATISTICAL VALIDATION REPORT ===\n")
            f.write(f"Parameters: {len(self.runs)} runs, Bonferroni alpha: {self.analysis['corrected_alpha']:.4f}\n\n")
            
            for metric, models in self.analysis["results"].items():
                f.write(f"METRIC: {metric.replace('_', ' ').upper()}\n")
                f.write("-" * 50 + "\n")
                
                rbdd = models["RBDD"]
                f.write(f"RBDD: Mean={rbdd['mean']:.2f}, CI={rbdd['ci_95']}\n\n")
                
                for base in self.baselines:
                    res = models[base]
                    status = "[SIGNIFICANT]" if res["significant"] else "[NOT SIGNIFICANT]"
                    f.write(f"  vs {base}:\n")
                    f.write(f"    p-value: {res['p_value']:.4e} {status}\n")
                    f.write(f"    Cohen's d: {res['cohens_d']:.2f}\n")
                    f.write(f"    95% CI: {res['ci_95']}\n")
                f.write("\n")

        logger.info(f"Statistical reports saved to {output_path} and {json_path}")
