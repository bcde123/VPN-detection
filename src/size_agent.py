#!/usr/bin/env python3
"""
Packet Size Analyzer
Analyzes packet size distributions and traffic volume patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import json
from pathlib import Path


def size_distribution_analysis(csv_path, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)

    # Estimate per-packet size (avg bytes per packet)
    df['avg_packet_size'] = df['byte_count'] / (df['packet_count'] + 1e-6)

    # Compute MTU proximity (e.g., 1400–1500 bytes common in VPN)
    df['near_mtu'] = df['avg_packet_size'].apply(lambda x: 1400 <= x <= 1500)

    # Basic stats
    mean_size = df['avg_packet_size'].mean()
    std_size = df['avg_packet_size'].std()
    mtu_ratio = df['near_mtu'].mean()

    # --- Plots ---
    # Histogram of packet sizes
    plt.figure(figsize=(6,4))
    plt.hist(df['avg_packet_size'], bins=20, alpha=0.7)
    plt.title('Packet Size Distribution')
    plt.xlabel('Average Packet Size (bytes)')
    plt.ylabel('Number of Flows')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/hist_packet_sizes.png")
    plt.close()

    # Heatmap of correlations between size & other metrics
    plt.figure(figsize=(6,4))
    sns.heatmap(df[['avg_packet_size','packet_count','byte_count','duration']].corr(),
                annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap (Size Features)')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/heatmap_size_features.png")
    plt.close()

    # Scatter: duration vs avg packet size
    plt.figure(figsize=(6,4))
    plt.scatter(df['duration'], df['avg_packet_size'], alpha=0.7)
    plt.title('Flow Duration vs Average Packet Size')
    plt.xlabel('Duration (s)')
    plt.ylabel('Avg Packet Size (bytes)')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/scatter_duration_size.png")
    plt.close()

    # --- Save summary JSON ---
    summary = {
        "mean_packet_size": float(mean_size),
        "std_packet_size": float(std_size),
        "vpn_like_flows_ratio": float(mtu_ratio),
        "total_flows": int(len(df))
    }

    print("[OK] Size Distribution Analysis Complete.")
    print(json.dumps(summary, indent=4))

    # Save JSON with filename expected by feature_engineering
    with open(f"{out_dir}/size_analysis.json", "w") as f:
        json.dump(summary, f, indent=4)
    print(f"[OK] Size summary JSON saved at {out_dir}/size_analysis.json")


def main():
    parser = argparse.ArgumentParser(description="Size Distribution Analysis Agent")
    parser.add_argument("--csv", required=True, help="Flow CSV input file")
    parser.add_argument("--out-dir", required=True, help="Output directory for results")
    args = parser.parse_args()

    size_distribution_analysis(args.csv, args.out_dir)


if __name__ == "__main__":
    main()
