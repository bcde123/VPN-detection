import pandas as pd
import os
import numpy as np
import json
import argparse

def compute_entropy(arr):
    """Compute normalized entropy of a 1D numeric array"""
    if len(arr) == 0:
        return 0
    value, counts = np.unique(arr, return_counts=True)
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def feature_engineering(flow_csv, temporal_json, size_json, tls_json, reputation_json, output_csv):
    # Load datasets
    flows = pd.read_csv(flow_csv)

    # --- Temporal features ---
    with open(temporal_json) as f:
        temporal = json.load(f)
    avg_interarrival = temporal.get("avg_mean_interarrival", 0)
    interarrival_var = temporal.get("avg_variance_interarrival", 0)
    burst_score = temporal.get("avg_burst_score", 0)

    # --- Size features ---
    with open(size_json) as f:
        size = json.load(f)
    mean_size = size.get("mean_packet_size", 0)
    std_size = size.get("std_packet_size", 0)

    # --- TLS features ---
    with open(tls_json) as f:
        tls = json.load(f)
    tls_unique_fp = tls.get("unique_fingerprints", 0)
    tls_suspicious_ratio = tls.get("suspicious_fingerprint_ratio", 0)

    # --- IP reputation features ---
    with open(reputation_json) as f:
        rep = json.load(f)
    vpn_like_ratio = rep.get("vpn_like_ips", 0) / max(rep.get("total_unique_ips", 1),1)
    local_ratio = rep.get("local_ips", 0) / max(rep.get("total_unique_ips", 1),1)

    # --- Compute per-flow entropy of packet sizes ---
    flows["packet_size_entropy"] = flows["byte_count"].apply(lambda x: compute_entropy([x]))

    # --- Add aggregated features ---
    flows["avg_interarrival"] = avg_interarrival
    flows["interarrival_var"] = interarrival_var
    flows["burst_score"] = burst_score
    flows["mean_packet_size"] = mean_size
    flows["std_packet_size"] = std_size
    flows["tls_unique_fp"] = tls_unique_fp
    flows["tls_suspicious_ratio"] = tls_suspicious_ratio
    flows["vpn_like_ip_ratio"] = vpn_like_ratio
    flows["local_ip_ratio"] = local_ratio

    # Normalize numeric features (simple min-max)
    numeric_cols = ["duration","packet_count","byte_count","avg_interarrival","interarrival_var",
                    "burst_score","mean_packet_size","std_packet_size",
                    "tls_unique_fp","tls_suspicious_ratio","vpn_like_ip_ratio","local_ip_ratio",
                    "packet_size_entropy"]
    for col in numeric_cols:
        flows[col] = (flows[col] - flows[col].min()) / (flows[col].max() - flows[col].min() + 1e-9)

    # Save ML-ready CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    flows.to_csv(output_csv, index=False)
    print(f"[OK] Feature engineering complete. ML-ready CSV saved at: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--flows", required=True, help="Input flows CSV")
    parser.add_argument("--temporal", required=True, help="Temporal JSON")
    parser.add_argument("--size", required=True, help="Size JSON")
    parser.add_argument("--tls", required=True, help="TLS JSON")
    parser.add_argument("--reputation", required=True, help="IP Reputation JSON")
    parser.add_argument("--out", required=True, help="Output ML-ready CSV")
    args = parser.parse_args()

    feature_engineering(
        flow_csv=args.flows,
        temporal_json=args.temporal,
        size_json=args.size,
        tls_json=args.tls,
        reputation_json=args.reputation,
        output_csv=args.out
    )
