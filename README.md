# Deep Packet Inspection (DPI) for VPN Detection

This project provides a **modular pipeline** for analyzing network traffic data, performing both **supervised** and **unsupervised** machine learning analysis to detect VPN and non-VPN traffic.  
The system automates the **PCAP processing → data preprocessing → feature extraction → model training** workflow with a single command.

## Quick Start

### **1️⃣ Setup Virtual Environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3️⃣ Prepare Data**

Place your PCAP files in the following directories:
- `data/NonVPN-PCAPs-01/` - Non-VPN traffic captures
- `data/VPN-PCAPS-01/` - VPN traffic captures

Or place pre-processed CSV files in `data/` directory.

### **4️⃣ Run the Complete Pipeline**

```bash
python run_pipeline.py
```

The script will automatically:
1. Convert PCAP files to CSV flows (if needed)
2. Preprocess the data
3. Extract multi-dimensional features
4. Train both supervised and unsupervised models


## 📁 Folder Structure

```
project_root/
│
├── data/
│   └── sample_flows.csv           # Raw network traffic input file
│
├── results/
│   ├── flow_analyzer/
│   ├── temporal_agent/
│   ├── size_agent/
│   ├── tls_analysis/
│   ├── reputation_analysis/
│   ├── ml_ready/
│   └── models/                    # Trained models stored here
│
├── src/
│   ├── pcap_to_csv.py              # Converts PCAP files to CSV flows
│   ├── preprocess_kaggle_traffic.py # Cleans and normalizes data
│   ├── flow_analyzer.py             # Flow-level statistics
│   ├── temporal_agent.py            # Temporal pattern analysis
│   ├── size_agent.py                # Packet size distribution
│   ├── tls_analysis.py              # TLS/SSL fingerprinting
│   ├── reputation_analysis.py       # IP reputation checking
│   ├── feature_engineering.py       # Feature aggregation
│   └── train_vpn_classifier.py      # Model training
│
├── requirements.txt
└── run_pipeline.py                  # Main orchestrator script
```


## Workflow Summary

| **Step** | **Script**                     | **Description**                                                                   |
| -------- | ------------------------------ | --------------------------------------------------------------------------------- |
| 1️⃣      | `pcap_to_csv.py`               | Converts raw PCAP files to CSV flow records using nfstream.                       |
| 2️⃣      | `preprocess_kaggle_traffic.py` | Cleans and normalizes flow data (CSV).                                            |
| 3️⃣      | `flow_analyzer.py`             | Analyzes flow-level statistics and stores summary JSON.                           |
| 4️⃣      | `reputation_analysis.py`       | Assesses IP/domain reputation from known threat lists.                            |
| 5️⃣      | `temporal_agent.py`            | Extracts temporal behavior patterns (e.g., packet timing, bursts).                |
| 6️⃣      | `size_agent.py`                | Analyzes packet size distributions and traffic volume.                            |
| 7️⃣      | `tls_analysis.py`              | Extracts SSL/TLS handshake and certificate features.                              |
| 8️⃣      | `feature_engineering.py`       | Merges all extracted features into a single ML-ready CSV.                         |
| 9️⃣      | `train_vpn_classifier.py`      | Trains models: supervised (VPN detection) & unsupervised (anomaly detection).     |
| 🚀      | `run_pipeline.py`              | Automatically executes all the above steps in sequence.                           |


## Machine Learning Models

* **Supervised Model:**
  Detects VPN vs Non-VPN traffic using labeled data (e.g., RandomForest, GradientBoost).
* **Unsupervised Model:**
  Identifies anomalies or unseen traffic patterns (e.g., IsolationForest, KMeans).

Trained models and evaluation metrics are saved in `results/models/`.


## Output Artifacts

| **File/Folder**                       | **Description**                                                |
| ------------------------------------- | -------------------------------------------------------------- |
| `results/ml_ready/flows_ml_ready.csv` | Final feature dataset used for ML.                             |
| `results/models/`                     | Trained models for supervised and unsupervised classification. |
| `results/*/summary.json`              | Intermediate reports for each module.                          |

---

## Notes

* Place your **raw traffic CSV** inside the `data/` folder before running the pipeline.
* Each stage logs progress and saves intermediate outputs in the `results/` directory.
* The `run_pipeline.py` script handles folder creation and file dependencies automatically.

---

## Manual Execution (for debugging individual steps)

```bash
# Step 1: Convert PCAP to CSV
python3 src/pcap_to_csv.py

# Step 2: Preprocess
python3 src/preprocess_kaggle_traffic.py --input data/combined_flows.csv --output data/processed_flows_1.csv

# Step 3: Flow Analysis
python3 src/flow_analyzer.py --csv data/processed_flows_1.csv --out-json results/flow_analyzer/summary.json

# Step 4: Reputation Analysis
python3 src/reputation_analysis.py --csv data/processed_flows_1.csv --out-json results/reputation_analysis/report.json

# Step 5: Temporal Analysis
python3 src/temporal_agent.py --csv data/processed_flows_1.csv --out-dir results/temporal_agent

# Step 6: Size Analysis
python3 src/size_agent.py --csv data/processed_flows_1.csv --out-dir results/size_agent

# Step 7: TLS Analysis
python3 src/tls_analysis.py --csv data/processed_flows_1.csv --out-dir results/tls_analysis

# Step 8: Feature Engineering
python3 src/feature_engineering.py \
  --flows data/processed_flows_1.csv \
  --temporal results/temporal_agent/temporal_summary.json \
  --size results/size_agent/size_analysis.json \
  --tls results/tls_analysis/tls_summary.json \
  --reputation results/reputation_analysis/report.json \
  --out results/ml_ready/flows_ml_ready.csv

# Step 9: Train Models
python3 src/train_vpn_classifier.py --csv results/ml_ready/flows_ml_ready.csv
```

---

## Final Output

After running the pipeline, your **trained models**, **reports**, and **feature datasets** will be available inside the `results/` folder, ready for evaluation or deployment.
