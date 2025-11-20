#!/usr/bin/env python3
"""
Data Preprocessor
Cleans and normalizes network traffic flow data.
"""

import pandas as pd
from pathlib import Path
import argparse

# --- Parse Arguments ---
parser = argparse.ArgumentParser(description="Preprocess traffic data")
parser.add_argument("--input", type=str, default="data/sample_flows.csv", help="Path to input CSV")
parser.add_argument("--output", type=str, default="data/processed_flows.csv", help="Path to output CSV")
args = parser.parse_args()

input_csv = args.input
output_csv = args.output

# --- Load dataset ---
df = pd.read_csv(input_csv)
print(f"[OK] Loaded {len(df)} records from {input_csv}")

# --- Check and rename columns to match pipeline ---
rename_map = {
    'source_ip': 'src_ip',
    'destination_ip': 'dst_ip',
    'source_port': 'src_port',
    'destination_port': 'dst_port',
    'protocol_type': 'protocol',
    'flow_duration': 'duration',
    'avg_packet_size': 'avg_packet_size',
    'packet_count': 'packet_count',
    'byte_count': 'byte_count',
    'label': 'label'
}

# Only rename columns that exist
df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)

# --- Create flow_id if not present ---
# Create flow_id only if src_ip and dst_ip exist
if 'src_ip' in df.columns and 'dst_ip' in df.columns:
    df['flow_id'] = df['src_ip'].astype(str) + '-' + df['dst_ip'].astype(str) + '-' + \
                    df['src_port'].astype(str) + '-' + df['dst_port'].astype(str) + '-' + \
                    df['protocol'].astype(str)
else:
    print("⚠️ src_ip/dst_ip columns not found — keeping existing flow_id.")
    if 'flow_id' not in df.columns:
        raise ValueError("Dataset missing both flow_id and IP columns.")


# --- Compute mean inter-arrival time if not present ---
if 'mean_interarrival' not in df.columns:
    df['mean_interarrival'] = df['duration'] / (df['packet_count'] + 1e-6)

# --- Save preprocessed CSV ---
Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_csv, index=False)
print(f"[OK] Preprocessed flows saved to {output_csv}")
print("Columns in output CSV:", list(df.columns))
print("Current columns:", list(df.columns.tolist()))
