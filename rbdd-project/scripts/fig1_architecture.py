"""Generates Figure 1: RBDD System Architecture diagram.

Uses Matplotlib to construct a professional workflow diagram for publication.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from loguru import logger

def create_architecture_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    color_header = '#003366'  # Navy
    color_box = '#E6F2FF'     # Light Blue
    color_decision = '#FFFFFF'
    color_allow = '#D4EDDA'   # Light Green
    color_deny = '#F8D7DA'    # Light Red
    
    # 1. User Request (Input)
    rect_user = patches.FancyBboxPatch((40, 90), 20, 6, boxstyle="round,pad=0.1", color=color_header, alpha=0.9)
    ax.add_patch(rect_user)
    ax.text(50, 93, 'User Request (Us_req)', color='white', ha='center', va='center', fontweight='bold')

    # 2. Access Trace Store
    ax.add_patch(patches.FancyBboxPatch((5, 75), 20, 8, boxstyle="round,pad=0.3", color=color_box, ec='gray'))
    ax.text(15, 79, 'Access Trace Store (ATr)\n{at1, at2, ..., atn}', ha='center', va='center', fontsize=9)

    # 3. ABM Module
    ax.add_patch(patches.Rectangle((35, 70), 30, 15, color=color_box, ec=color_header, lw=2))
    ax.text(50, 82, 'ABM: Access Restricted Module', fontweight='bold', ha='center')
    ax.text(50, 75, 'Measure = (NoSA/Tac) * (NUFP/Tbac) * (Tup/Tac)', ha='center', fontsize=8, style='italic')

    # 3b. ABM Decision
    ax.add_patch(patches.RegularPolygon((50, 62), numVertices=4, radius=6, color=color_decision, ec='black'))
    ax.text(50, 62, '>= 0.8?', ha='center', va='center', fontweight='bold', fontsize=8)

    # 4. Deny Path
    ax.annotate('NO', xy=(44, 62), xytext=(30, 62), arrowprops=dict(arrowstyle='->'))
    ax.add_patch(patches.Rectangle((10, 58), 20, 8, color=color_deny, ec='red'))
    ax.text(20, 62, 'ACCESS DENIED\n(Side-Channel Threat)', ha='center', va='center', color='darkred', fontsize=8, fontweight='bold')

    # 5. Allow Path -> BLRM
    ax.annotate('YES', xy=(50, 56), xytext=(50, 50), arrowprops=dict(arrowstyle='->'))
    
    # 5. Page Matrix Store
    ax.add_patch(patches.FancyBboxPatch((75, 45), 20, 8, boxstyle="round,pad=0.3", color=color_box, ec='gray'))
    ax.text(85, 49, 'Page Matrix (PM)\nMetadata Registry', ha='center', va='center', fontsize=9)

    # 6. BLRM Module
    ax.add_patch(patches.Rectangle((35, 35), 30, 15, color=color_box, ec=color_header, lw=2))
    ax.text(50, 47, 'BLRM: Data Deduplication', fontweight='bold', ha='center')
    ax.text(50, 40, 'Score = CBS(Bi) * PBS(Bi)', ha='center', fontsize=8, style='italic')

    # 6b. BLRM Decision
    ax.add_patch(patches.RegularPolygon((50, 27), numVertices=4, radius=6, color=color_decision, ec='black'))
    ax.text(50, 27, '>= 0.6?', ha='center', va='center', fontweight='bold', fontsize=8)

    # 7. Duplicate Path
    ax.annotate('DUPLICATE', xy=(65, 27), xytext=(80, 27), arrowprops=dict(arrowstyle='->'))
    ax.add_patch(patches.Rectangle((75, 23), 20, 8, color='#FFF3CD', ec='orange'))
    ax.text(85, 27, 'BLOCK REMOVED', ha='center', va='center', color='brown', fontsize=8, fontweight='bold')

    # 8. Unique Path -> Dual Encryption
    ax.annotate('UNIQUE', xy=(50, 21), xytext=(50, 15), arrowprops=dict(arrowstyle='->'))
    
    ax.add_patch(patches.Rectangle((35, 5), 30, 12, color=color_allow, ec='green', lw=2))
    ax.text(50, 14, 'Dual-Mode Encryption', fontweight='bold', ha='center')
    ax.text(50, 10, 'Layer 1: System Key (Session)\nLayer 2: User-Specific Key', ha='center', fontsize=8)

    # 9. Cloud Storage
    ax.annotate('', xy=(50, 0), xytext=(50, 5), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(50, -2, 'CLOUD STORAGE (Encrypted)', ha='center', fontweight='bold', color=color_header)

    # Connectors for data stores
    ax.annotate('', xy=(40, 78), xytext=(25, 79), arrowprops=dict(arrowstyle='<-', ls='--'))
    ax.annotate('', xy=(65, 46), xytext=(75, 48), arrowprops=dict(arrowstyle='<-', ls='--'))

    # Title
    ax.text(50, 105, 'FIGURE 1: RBDD SYSTEM ARCHITECTURE', ha='center', fontsize=16, fontweight='bold', color=color_header)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight')
    plt.close()
    logger.info(f"Figure 1 saved to {output_path}")

if __name__ == "__main__":
    create_architecture_diagram("reports/figures/fig1_rbdd_architecture.png")
