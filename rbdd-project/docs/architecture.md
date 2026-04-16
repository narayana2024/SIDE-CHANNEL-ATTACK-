# Architecture

The system follows a modular architecture containing these primary stages:
- **Data Generation**: Produces synthetic cloud access traces.
- **Access Control (ABM)**: Evaluates attribute metrics.
- **Deduplication (BLRM)**: Performs Block-Level Data De-duplication.
- **Dual-Encryption**: Employs rotating keys per specific sessions.
- **Baselines Contextualizing**: Exposes identical interfaces to execute MLE, MPT, SD2M implementations parallel to RBDD for benchmarking.
- **Reporting & Evaluation**: Automates statistically robust significance tests and auto-generates paper matching charts.
