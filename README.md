# RBDD — Real-Time Block-Level Dual-Mode Data Deduplication

This repository contains the implementation of the RBDD framework designed to mitigate side-channel attacks in Cloud Storage.

## Research Domain
Cloud Security & Data Deduplication

## Novel Contributions
- **ABM (Attribute-Based Mechanism):** Access restriction logic to constrain unauthorized user entries.
- **BLRM (Block-Level Matching Method):** Block-level deduplication approach enhancing storage utilization.
- **Dual-Mode Encryption:** Integration of session-rotating system keys to minimize side-channel vulnerability.

## Setup
1. Create a Python 3.10+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the main script to start simulations and recreate published results.
```bash
python main.py --help
```
