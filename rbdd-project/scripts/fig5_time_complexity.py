"""Generates Figure 5: Analysis on Time Consumption grouped bar chart.

Reproduces the time complexity comparison between RBDD and baseline modules
using values from Table 5 of the paper.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from loguru import logger
from config.published_results import TABLE_5_TIME_COMPLEXITY

def generate_figure5(output_dir: str):
    # Data Extraction (Note: Table 5 has blocks in [200, 150, 100, 50] order)
    # We sort them for the chart [50, 100, 150, 200]
    raw_blocks = TABLE_5_TIME_COMPLEXITY["blocks"]
    raw_mle = TABLE_5_TIME_COMPLEXITY["MLE"]
    raw_mpt = TABLE_5_TIME_COMPLEXITY["MPT"]
    raw_sd2m = TABLE_5_TIME_COMPLEXITY["SD2M"]
    raw_rbdd = TABLE_5_TIME_COMPLEXITY["RBDD"]

    # Re-ordering for ascending x-axis
    sorted_indices = np.argsort(raw_blocks)
    blocks = [raw_blocks[i] for i in sorted_indices]
    mle = [raw_mle[i] for i in sorted_indices]
    mpt = [raw_mpt[i] for i in sorted_indices]
    sd2m = [raw_sd2m[i] for i in sorted_indices]
    rbdd = [raw_rbdd[i] for i in sorted_indices]

    # Setup
    x = np.arange(len(blocks))
    width = 0.18
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Bars
    rects1 = ax.bar(x - 1.5*width, mle, width, label='MLE', color='coral', edgecolor='black', alpha=0.8)
    rects2 = ax.bar(x - 0.5*width, mpt, width, label='MPT', color='orange', edgecolor='black', alpha=0.8)
    rects3 = ax.bar(x + 0.5*width, sd2m, width, label='SD2M', color='steelblue', edgecolor='black', alpha=0.8)
    rects4 = ax.bar(x + 1.5*width, rbdd, width, label='RBDD', color='darkgreen', edgecolor='black', linewidth=1.5)

    # Formatting
    ax.set_xlabel('No. of Blocks', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time Complexity (Seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Analysis on Time Consumption', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(blocks)
    ax.set_ylim(0, 75)
    ax.legend(loc='upper left', frameon=True, fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Label values on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}s',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    autolabel(rects4)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    out_png = os.path.join(output_dir, "fig5_time_complexity.png")
    out_pdf = os.path.join(output_dir, "fig5_time_complexity.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    logger.info(f"Figure 5 saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Generate Figure 5 for RBDD paper.")
    parser.add_argument("--output-dir", type=str, default="reports/figures")
    args = parser.parse_args()
    generate_figure5(args.output_dir)

if __name__ == "__main__":
    main()
