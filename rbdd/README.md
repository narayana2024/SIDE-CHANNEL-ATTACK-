# RBDD: Real-Time Block-Level Dual-Mode Data Deduplication Framework

A fully reproducible research implementation of the RBDD framework for secure and efficient cloud data deduplication. This project faithfully reproduces the results, tables, and figures published in the target SCI-indexed research paper.

## 🚀 Key Features

*   **ABM (Access Behavioral Measure)**: 3-factor access restriction based on response state, protocol compliance, and update intensity.
*   **BLRM (Block-Level Relational Measure)**: Advanced multi-stage deduplication using CBS (Complete Block Similarity) and PBS (Partial Block Similarity).
*   **Dual-Mode Encryption**: Secure two-layer protection using dynamic session keys and user-specific secrets to mitigate side-channel attacks.
*   **Statistical Rigor**: Integrated t-tests, bootstrap confidence intervals, and Bonferroni corrections.
*   **Publication Ready**: Automated generation of LaTeX tables, PNG charts, and high-resolution architecture diagrams.

## 📁 Repository Structure

```text
rbdd-project/
├── config/             # Global settings and publication ground-truth
├── reports/            # Generated figures, tables, and statistical results
├── scripts/            # Visualization and simulation runners
├── src/
│   ├── data/           # Data structures (ATr, PM, Synthetic Gen)
│   ├── models/         # Implementation of RBDD and Baselins (MLE, MPT, SD2M)
│   └── evaluation/     # Metrics, Simulator, and Statistical tests
└── tests/              # Comprehensive pytest suite
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rbdd-project
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

## 📊 Running the Reproduction Pipeline

To reproduce all results, tables, and figures with a single command:

```bash
python master_reproduction.py
```

This script will:
1. Generate synthetic experimental data.
2. Run simulations for RBDD and 3 baseline models across all scales.
3. Validate computed results against the published ground truth.
4. Perform 10-run statistical significance testing.
5. Generate all 5 publication figures + 2 advanced summary plots.
6. Export all results to LaTeX and PNG formats.

## 📈 Performance Summary (N=200)

| Metric | RBDD | MLE | MPT | SD2M |
| :--- | :--- | :--- | :--- | :--- |
| **Access Restriction** | **97.0%** | 76.0% | 82.0% | 85.0% |
| **Data Deduplication** | **95.0%** | 71.0% | 76.0% | 81.0% |
| **Security Analysis** | **95.0%** | 72.0% | 78.0% | 83.0% |
| **Time Complexity** | **23.0s** | 62.0s | 58.0s | 52.0s |

## 🧪 Testing

Run the test suite to ensure code integrity:
```bash
pytest tests/
```

## 📜 License

This project is released under the MIT License for academic and research use.
