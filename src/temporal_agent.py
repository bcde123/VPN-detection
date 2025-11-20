#!/usr/bin/env python3
"""
Temporal Pattern Analyzer
Analyzes timing patterns, inter-arrival times, and burst behavior in network traffic.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from pathlib import Path
from scipy.stats import entropy


def temporal_analysis(csv_path, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)

    # Compute additional temporal features
    df['interarrival_var'] = df['mean_interarrival'].rolling(window=3, min_periods=1).var()
    df['interarrival_entropy'] = entropy(df['mean_interarrival'].value_counts(normalize=True), base=2)

    # Detect potential bursts (short flows with many packets)
    df['burst_score'] = (df['packet_count'] / (df['duration'] + 1e-6))  # packets/sec

    # Visualization 1: Heatmap of inter-arrival time distributions
    plt.figure(figsize=(8, 5))
    sns.heatmap(df[['mean_interarrival', 'duration', 'packet_count']].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap: Temporal Features')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/heatmap_interarrival.png")
    plt.close()

    # Visualization 2: Scatter plot (flow duration vs. packet count)
    plt.figure(figsize=(6, 4))
    plt.scatter(df['duration'], df['packet_count'], alpha=0.7)
    plt.title('Flow Duration vs Packet Count')
    plt.xlabel('Duration (sec)')
    plt.ylabel('Packet Count')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/scatter_duration_packets.png")
    plt.close()

    # Visualization 3: Histogram of mean interarrival times
    plt.figure(figsize=(6, 4))
    plt.hist(df['mean_interarrival'], bins=20, alpha=0.7)
    plt.title('Histogram of Mean Inter-arrival Times')
    plt.xlabel('Inter-arrival Time (s)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/hist_interarrival.png")
    plt.close()

    # Save stats summary
    summary = {
        "avg_mean_interarrival": float(df['mean_interarrival'].mean()),
        "avg_variance_interarrival": float(df['interarrival_var'].mean()),
        "avg_entropy": float(df['interarrival_entropy'].mean()),
        "avg_burst_score": float(df['burst_score'].mean())
    }

    print("[OK] Temporal Analysis Complete.")
    print(summary)

    with open(f"{out_dir}/temporal_summary.json", "w") as f:
        import json
        json.dump(summary, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Temporal Pattern Analysis Agent")
    parser.add_argument("--csv", required=True, help="Flow CSV input file")
    parser.add_argument("--out-dir", required=True, help="Output directory for results")
    args = parser.parse_args()

    temporal_analysis(args.csv, args.out_dir)


if __name__ == "__main__":
    main()
