"""Generates Figure 3: Analysis on Data Deduplication Performance grouped bar chart.

Reproduces the comparison between RBDD and baseline modules (MLE, MPT, SD2M)
using values from Table 3 of the paper.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from loguru import logger
from config.published_results import TABLE_3_DATA_DEDUPLICATION

def generate_figure3(output_dir: str):
    # Data Extraction
    blocks = TABLE_3_DATA_DEDUPLICATION["blocks"]
    mle = TABLE_3_DATA_DEDUPLICATION["MLE"]
    mpt = TABLE_3_DATA_DEDUPLICATION["MPT"]
    sd2m = TABLE_3_DATA_DEDUPLICATION["SD2M"]
    rbdd = TABLE_3_DATA_DEDUPLICATION["RBDD"]

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
    ax.set_ylabel('Data Deduplication Performance (%)', fontsize=12, fontweight='bold')
    ax.set_title('Analysis on Data Deduplication Performance', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(blocks)
    ax.set_ylim(50, 105)
    ax.legend(loc='upper left', frameon=True, fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Label values on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
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
    out_png = os.path.join(output_dir, "fig3_data_deduplication.png")
    out_pdf = os.path.join(output_dir, "fig3_data_deduplication.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    logger.info(f"Figure 3 saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Generate Figure 3 for RBDD paper.")
    parser.add_argument("--output-dir", type=str, default="reports/figures")
    args = parser.parse_args()
    generate_figure3(args.output_dir)

if __name__ == "__main__":
    main()
