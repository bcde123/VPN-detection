# : Deep Packet Inspection (DPI) Agents for Encrypted Traffic

This project provides a **modular pipeline** for analyzing network traffic data, performing both **supervised** and **unsupervised** machine learning analysis to detect VPN and non-VPN traffic.  
The system automates the **data preprocessing → feature extraction → model training** workflow with a single command.

### **1️⃣ Setup Virtual Environment**

```bash
python -m venv venv

.\venv\Scripts\Activate.ps1

# macos
source venv/bin/activate
````

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3️⃣ Run the Complete Pipeline**

```bash
python3 ./run_pipeline.py
```

The script will automatically process your input data, extract features, and train both supervised and unsupervised models.


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
│   ├── preprocess_kaggle_traffic.py
│   ├── flow_analyzer.py
│   ├── temporal_agent.py
│   ├── size_agent.py
│   ├── tls_analysis.py
│   ├── reputation_analysis.py
│   ├── feature_engineering.py
│   ├── train_vpn_classifier.py
│   
│
└── requirements.txt
└── run_pipeline.py            # Main orchestrator script
```


## Workflow Summary

| **Step** | **Script**                     | **Description**                                                                   |
| -------- | ------------------------------ | --------------------------------------------------------------------------------- |
| 1️⃣      | `preprocess_kaggle_traffic.py` | Cleans and normalizes raw flow data (CSV).                                        |
| 2️⃣      | `flow_analyzer.py`             | Analyzes flow-level statistics and stores summary JSON.                           |
| 3️⃣      | `temporal_agent.py`            | Extracts temporal behavior patterns (e.g., packet timing).                        |
| 4️⃣      | `size_agent.py`                | Analyzes packet size distributions and traffic volume.                            |
| 5️⃣      | `tls_analysis.py`              | Extracts SSL/TLS handshake and certificate features.                              |
| 6️⃣      | `reputation_analysis.py`       | Assesses IP/domain reputation from known threat lists.                            |
| 7️⃣      | `feature_engineering.py`       | Merges all extracted features into a single ML-ready CSV.                         |
| 8️⃣      | `train_vpn_classifier.py`      | Trains two models: supervised (VPN detection) & unsupervised (anomaly detection). |
| 9️⃣      | `run_pipeline.py`              | Automatically runs all the above steps in order.                                  |


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

## Example Command Sequence (for manual debugging)

```bash
python src/preprocess_kaggle_traffic.py --input data/sample_flows.csv --output data/processed_flows.csv
python src/flow_analyzer.py --csv data/processed_flows.csv --out-json results/flow_analyzer/summary.json
python src/temporal_agent.py --csv data/processed_flows.csv --out-dir results/temporal_agent
python src/size_agent.py --csv data/processed_flows.csv --out-dir results/size_agent
python src/tls_analysis.py --csv data/processed_flows.csv --out-dir results/tls_analysis
python src/reputation_analysis.py --csv data/processed_flows.csv --out-json results/reputation_analysis/report.json
python src/feature_engineering.py --flows data/processed_flows.csv --temporal results/temporal_agent/temporal_summary.json --size results/size_agent/size_analysis.json --tls results/tls_analysis/tls_summary.json --reputation results/reputation_analysis/report.json --out results/ml_ready/flows_ml_ready.csv
python src/train_vpn_classifier.py --csv results/ml_ready/flows_ml_ready.csv
```

---

## Final Output

After running the pipeline, your **trained models**, **reports**, and **feature datasets** will be available inside the `results/` folder, ready for evaluation or deployment.
