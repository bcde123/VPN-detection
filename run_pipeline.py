import subprocess
import os

# Paths
# data_csv = "data/sample_flows_1.csv" # Old CSV input
data_csv = "data/combined_flows.csv"   # New CSV input from PCAPs
processed_csv = "data/processed_flows_1.csv"

# Results directories
results_dir = "results"
temporal_dir = os.path.join(results_dir, "temporal_agent")
size_dir = os.path.join(results_dir, "size_agent")
tls_dir = os.path.join(results_dir, "tls_analysis")
reputation_dir = os.path.join(results_dir, "reputation_analysis")
ml_ready_csv = os.path.join(results_dir, "ml_ready", "flows_ml_ready.csv")

def run_command(cmd):
    print(f"\n[RUNNING] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        exit(1)

def main():
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(os.path.dirname(ml_ready_csv), exist_ok=True)
    
    # 0. Convert PCAPs to CSV
    run_command("python src/pcap_to_csv.py")

    # 1. Preprocess flows
    run_command(f"python src/preprocess_kaggle_traffic.py --input {data_csv} --output {processed_csv}")

    # 2. Flow analyzer
    run_command(f"python src/flow_analyzer.py --csv {processed_csv} --out-json {os.path.join(results_dir,'flow_analyzer','summary.json')}")

    # 3. Temporal features
    run_command(f"python src/temporal_agent.py --csv {processed_csv} --out-dir {temporal_dir}")

    # 4. Size features
    run_command(f"python src/size_agent.py --csv {processed_csv} --out-dir {size_dir}")

    # 5. TLS analysis
    run_command(f"python src/tls_analysis.py --csv {processed_csv} --out-dir {tls_dir}")

    # 6. Reputation analysis
    run_command(f"python src/reputation_analysis.py --csv {processed_csv} --out-json {os.path.join(reputation_dir,'report.json')}")

    # 7. Feature engineering
    run_command(
        f"python src/feature_engineering.py "
        f"--flows {processed_csv} "
        f"--temporal {os.path.join(temporal_dir,'temporal_summary.json')} "
        f"--size {os.path.join(size_dir,'size_analysis.json')} "
        f"--tls {os.path.join(tls_dir,'tls_summary.json')} "
        f"--reputation {os.path.join(reputation_dir,'report.json')} "
        f"--out {ml_ready_csv}"
    )

    # 8. Train VPN classifier
    run_command(f"python src/train_vpn_classifier.py --csv {ml_ready_csv}")

    print("\n[OK] Full pipeline executed successfully!")

if __name__ == "__main__":
    main()
