import pandas as pd
import argparse
import json
from pathlib import Path
import numpy as np

def analyze_flows(csv_path, out_json):
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} flows from {csv_path}")
    print("\nColumns:", list(df.columns))

    # --- Basic metrics ---
    total_bytes = df['byte_count'].sum()
    total_packets = df['packet_count'].sum()
    avg_duration = df['duration'].mean()
    top_ports = df['dst_port'].value_counts().head(5).to_dict()

    # --- Temporal metrics ---
    # mean and variance of interarrival times
    avg_mean_interarrival = df['mean_interarrival'].mean() if 'mean_interarrival' in df.columns else 0
    avg_variance_interarrival = df['mean_interarrival'].var() if 'mean_interarrival' in df.columns else 0

    # simple entropy of packet counts per flow
    if 'packet_count' in df.columns:
        packet_counts = df['packet_count'].values
        counts, freq = np.unique(packet_counts, return_counts=True)
        probs = freq / freq.sum()
        avg_entropy = -np.sum(probs * np.log2(probs))
    else:
        avg_entropy = 0

    # simple burst score: sum(packet_count / duration)
    burst_score = (df['packet_count'] / df['duration'].replace(0,1)).sum() if 'packet_count' in df.columns and 'duration' in df.columns else 0

    # --- Build report ---
    report = {
        "total_flows": len(df),
        "total_bytes": int(total_bytes),
        "total_packets": int(total_packets),
        "average_duration_sec": round(avg_duration, 4),
        "top_destination_ports": top_ports,
        "avg_mean_interarrival": float(avg_mean_interarrival),
        "avg_variance_interarrival": float(avg_variance_interarrival),
        "avg_entropy": float(avg_entropy),
        "avg_burst_score": float(burst_score)
    }

    # Save to JSON
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(report, f, indent=4)

    print("\n[OK] Analysis complete. Saved summary to:", out_json)
    print(json.dumps(report, indent=4))


def main():
    parser = argparse.ArgumentParser(description="Analyze extracted network flow data with temporal features")
    parser.add_argument("--csv", required=True, help="Input flow CSV file")
    parser.add_argument("--out-json", required=True, help="Output JSON summary path")
    args = parser.parse_args()
    analyze_flows(args.csv, args.out_json)

if __name__ == "__main__":
    main()
