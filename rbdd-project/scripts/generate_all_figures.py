"""Master script to generate all publication figures for the RBDD project.

Orchestrates everything from architecture diagrams to comparative bar charts
and advanced statistical visualizations.
"""

import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
import pandas as pd
import seaborn as sns

# Import individual figure generators
from scripts.fig1_architecture import create_architecture_diagram
from scripts.fig2_access_restriction import generate_figure2
from scripts.fig3_deduplication import generate_figure3
from scripts.fig4_encryption import generate_figure4
from scripts.fig5_time_complexity import generate_figure5

# Import results for radar and heatmap
from config.published_results import (
    TABLE_2_ACCESS_RESTRICTION,
    TABLE_3_DATA_DEDUPLICATION,
    TABLE_4_ENCRYPTION_DECRYPTION,
    TABLE_5_TIME_COMPLEXITY
)

def generate_radar_chart(output_path: str):
    """Produces a radar chart comparing models across all metrics at max scale (N=200)."""
    labels = ['Access Restriction', 'Deduplication', 'Security/Enc', 'Efficiency (1/Time)']
    models = ["RBDD", "MLE", "MPT", "SD2M"]
    colors = ['darkgreen', 'coral', 'orange', 'steelblue']
    
    # Normalize data (0-100)
    # For time, we use (max_time - actual_time) / max_time * 100 as an efficiency metric
    max_t = 65.0
    
    data = {}
    for m in models:
        acc = TABLE_2_ACCESS_RESTRICTION[m][-1]
        ded = TABLE_3_DATA_DEDUPLICATION[m][-1]
        enc = TABLE_4_ENCRYPTION_DECRYPTION[m][-1]
        # Table 5 at 200 blocks
        t_val = TABLE_5_TIME_COMPLEXITY[m][TABLE_5_TIME_COMPLEXITY["blocks"].index(200)]
        eff = ((max_t - t_val) / max_t) * 100
        data[m] = [acc, ded, enc, eff]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1] # Close the circle

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for i, model in enumerate(models):
        values = data[model]
        values += values[:1]
        ax.plot(angles, values, color=colors[i], linewidth=2, label=model)
        ax.fill(angles, values, color=colors[i], alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Holistic Performance Comparison (N=200)", pad=20, fontweight='bold')
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Radar chart saved to {output_path}")

def generate_improvement_heatmap(output_path: str):
    """Generates a heatmap of % improvement of RBDD over baselines."""
    models = ["MLE", "MPT", "SD2M"]
    metrics = ["Access Restriction", "Deduplication", "Encryption", "Time Efficiency"]
    
    improvement_data = []
    
    for m in models:
        row = []
        # Access
        rbdd_acc = TABLE_2_ACCESS_RESTRICTION["RBDD"][-1]
        m_acc = TABLE_2_ACCESS_RESTRICTION[m][-1]
        row.append(((rbdd_acc - m_acc) / m_acc) * 100)
        
        # Dedup
        rbdd_ded = TABLE_3_DATA_DEDUPLICATION["RBDD"][-1]
        m_ded = TABLE_3_DATA_DEDUPLICATION[m][-1]
        row.append(((rbdd_ded - m_ded) / m_ded) * 100)
        
        # Enc
        rbdd_enc = TABLE_4_ENCRYPTION_DECRYPTION["RBDD"][-1]
        m_enc = TABLE_4_ENCRYPTION_DECRYPTION[m][-1]
        row.append(((rbdd_enc - m_enc) / m_enc) * 100)
        
        # Time (Lower is better, so improvement is (old-new)/old)
        rbdd_t = 23.0
        idx = TABLE_5_TIME_COMPLEXITY["blocks"].index(200)
        m_t = TABLE_5_TIME_COMPLEXITY[m][idx]
        row.append(((m_t - rbdd_t) / m_t) * 100)
        
        improvement_data.append(row)

    df = pd.DataFrame(improvement_data, index=models, columns=metrics)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(df, annot=True, fmt=".1f", cmap="YlGn", cbar_kws={'label': '% Improvement'})
    plt.title("RBDD Performance Gain Over Baselines (%)", fontweight='bold', pad=15)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Heatmap saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate all publication-quality figures.")
    parser.add_argument("--output-dir", type=str, default="reports/figures")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    logger.info("Starting Master Figure Generation...")
    
    # 1. Individual Paper Figures
    create_architecture_diagram(os.path.join(args.output_dir, "fig1_rbdd_architecture.png"))
    generate_figure2(args.output_dir)
    generate_figure3(args.output_dir)
    generate_figure4(args.output_dir)
    generate_figure5(args.output_dir)
    
    # 2. Advanced Summary Visualizations
    generate_radar_chart(os.path.join(args.output_dir, "radar_comparison.png"))
    generate_improvement_heatmap(os.path.join(args.output_dir, "improvement_heatmap.png"))
    
    logger.success("All 7 figures generated successfully in " + args.output_dir)

if __name__ == "__main__":
    main()
