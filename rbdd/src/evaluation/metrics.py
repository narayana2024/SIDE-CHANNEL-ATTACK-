"""Evaluation metrics for RBDD and baseline comparisons.

Implements the four core metrics defined in the research paper:
Access Restriction, Data Deduplication, Encryption/Decryption Security, 
and Time Complexity.
"""

import time
from typing import Dict, List, Any, Optional
from loguru import logger
from tabulate import tabulate
import matplotlib.pyplot as plt

def compute_access_restriction(identified: int, total_malicious: int) -> float:
    """Metric 1: Access Restriction Performance (%).
    
    Formula: (Number of Malicious Requests Identified / Total Malicious Received) * 100
    """
    if total_malicious == 0:
        return 100.0  # Or 0, depends on interpretation; if no threats, performance is perfect.
    return (identified / total_malicious) * 100

def compute_deduplication_performance(identified: int, total_duplicates: int) -> float:
    """Metric 2: Data Deduplication Performance (%).
    
    Formula: (Number of Duplicate Blocks Identified / Total Duplicate Submitted) * 100
    """
    if total_duplicates == 0:
        return 100.0
    return (identified / total_duplicates) * 100

def compute_encryption_performance(secure_blocks: int, total_blocks: int) -> float:
    """Metric 3: Encryption/Decryption Performance (%).
    
    Formula: (Blocks Not Compromised / Total Blocks Given) * 100
    """
    if total_blocks == 0:
        return 100.0
    return (secure_blocks / total_blocks) * 100

def compute_time_complexity(start_time: float, end_time: float) -> float:
    """Metric 4: Time Complexity (seconds)."""
    return max(0.0, end_time - start_time)

def format_results_table(results: Dict[str, Dict[str, float]], title: str = "Results Summary") -> str:
    """Formats a results dictionary into a pretty-print table."""
    headers = ["Metric", "RBDD", "MLE", "MPT", "SD2M"]
    table_data = []
    
    # We assume metrics as keys: access_restriction, deduplication, etc.
    metrics_map = {
        "access_restriction": "Access Restriction (%)",
        "deduplication": "Data Deduplication (%)",
        "encryption": "Encryption/Decryption (%)",
        "time": "Time Complexity (s)"
    }
    
    for m_key, m_name in metrics_map.items():
        row = [m_name]
        for model in ["RBDD", "MLE", "MPT", "SD2M"]:
            val = results.get(m_key, {}).get(model, 0.0)
            row.append(f"{val:.2f}")
        table_data.append(row)
        
    return f"\n{title}\n" + tabulate(table_data, headers=headers, tablefmt="grid")

def export_latex_table(results: Dict[str, Dict[str, float]], caption: str) -> str:
    """Exports results to a LaTeX table format."""
    headers = ["Metric", "RBDD", "MLE", "MPT", "SD2M"]
    table_data = []
    metrics_map = {
        "access_restriction": "Access Restriction (\\%)",
        "deduplication": "Data Deduplication (\\%)",
        "encryption": "Encryption/Decryption (\\%)",
        "time": "Time Complexity (s)"
    }
    
    for m_key, m_name in metrics_map.items():
        row = [m_name]
        for model in ["RBDD", "MLE", "MPT", "SD2M"]:
            val = results.get(m_key, {}).get(model, 0.0)
            row.append(f"{val:.2f}")
        table_data.append(" & ".join(row) + " \\\\")

    latex = [
        "\\begin{table}[h!]",
        "\\centering",
        f"\\caption{{{caption}}}",
        "\\begin{tabular}{|l|c|c|c|c|}",
        "\\hline",
        " & ".join(headers) + " \\\\",
        "\\hline"
    ]
    latex.extend(table_data)
    latex.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}"
    ])
    return "\n".join(latex)

def export_table_as_png(results: Dict[str, Dict[str, float]], title: str, output_path: str):
    """Renders a results dictionary as a PNG image table."""
    headers = ["Metric", "RBDD", "MLE", "MPT", "SD2M"]
    table_data = []
    metrics_map = {
        "access_restriction": "Access Restriction (%)",
        "deduplication": "Data Deduplication (%)",
        "encryption": "Encryption/Decryption (%)",
        "time": "Time Complexity (s)"
    }
    
    for m_key, m_name in metrics_map.items():
        row = [m_name]
        for model in ["RBDD", "MLE", "MPT", "SD2M"]:
            val = results.get(m_key, {}).get(model, 0.0)
            row.append(f"{val:.2f}")
        table_data.append(row)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    
    table = ax.table(cellText=[headers] + table_data, loc='center', cellLoc='center', colWidths=[0.3, 0.15, 0.15, 0.15, 0.15])
    
    # Styling
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Bold headers
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_text_props(fontweight='bold', color='white')
            cell.set_facecolor('#003366')
        elif j == 0:
            cell.set_text_props(fontweight='bold')

    plt.title(title, fontweight='bold', pad=10)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Table PNG saved to {output_path}")

def validate_against_published(computed: Dict[str, float], published: Dict[str, float], 
                               tolerance: float = 0.5) -> bool:
    """Validates if computed results are within tolerance of published results.
    
    Args:
        computed: Dictionary of computed metrics.
        published: Dictionary of expected metrics.
        tolerance: Allowed difference percentage point (default 0.5).
        
    Returns:
        bool: True if all match within tolerance.
    """
    match = True
    for key, expected_val in published.items():
        if key not in computed:
            logger.warning(f"Validation: Metric {key} missing from computed results.")
            match = False
            continue
            
        actual_val = computed[key]
        diff = abs(actual_val - expected_val)
        if diff > tolerance:
            logger.error(f"Validation FAILED for {key}: Published {expected_val}, Computed {actual_val} (Diff: {diff:.2f})")
            match = False
        else:
            logger.success(f"Validation PASSED for {key}: Published {expected_val}, Computed {actual_val}.")
            
    return match
