#!/usr/bin/env python3
"""
VPN Detection Pipeline
Automated execution of all analysis steps from PCAP processing to ML model training.
"""

import os
import subprocess
import sys

def run_command(description, command):
    """Execute a command and handle errors."""
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"{'='*80}")
    print(f"Command: {command}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False, text=True)
        print(f"✓ {description} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}\n")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              VPN DETECTION PIPELINE - AUTOMATED EXECUTION                  ║
║           PCAP Processing → Feature Extraction → Model Training            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    steps = [
        ("1. Convert PCAP files to CSV",
         "python src/pcap_to_csv.py"),
        
        ("2. Preprocess flows",
         "python src/preprocess_kaggle_traffic.py --input data/combined_flows.csv --output data/processed_flows_1.csv"),
        
        ("3. Analyze flow patterns",
         "python src/flow_analyzer.py --csv data/processed_flows_1.csv --out-json results/flow_analyzer/summary.json"),
        
        ("4. Analyze IP reputation",
         "python src/reputation_analysis.py --csv data/processed_flows_1.csv --out-json results/reputation_analysis/report.json"),
        
        ("5. Analyze temporal patterns",
         "python src/temporal_agent.py --csv data/processed_flows_1.csv --out-dir results/temporal_agent"),
        
        ("6. Analyze packet sizes",
         "python src/size_agent.py --csv data/processed_flows_1.csv --out-dir results/size_agent"),
        
        ("7. Analyze TLS fingerprints",
         "python src/tls_analysis.py --csv data/processed_flows_1.csv --out-dir results/tls_analysis"),
        
        ("8. Generate ML-ready features",
         """python src/feature_engineering.py \
--flows data/processed_flows_1.csv \
--temporal results/temporal_agent/temporal_summary.json \
--size results/size_agent/size_analysis.json \
--tls results/tls_analysis/tls_summary.json \
--reputation results/reputation_analysis/report.json \
--out results/ml_ready/flows_ml_ready.csv"""),
    ]
    
    failed_steps = []
    
    for description, command in steps:
        if not run_command(description, command):
            failed_steps.append(description)
            response = input("\n⚠ Continue despite error? (y/n): ").strip().lower()
            if response != 'y':
                print("\n❌ Pipeline execution aborted.")
                sys.exit(1)
    
    print("\n" + "="*80)
    if failed_steps:
        print(f"⚠ Pipeline completed with {len(failed_steps)} error(s):")
        for step in failed_steps:
            print(f"  - {step}")
    else:
        print("✓ ALL STEPS COMPLETED SUCCESSFULLY!")
    print("="*80)
    
    print("\n📊 Final Output:")
    print("   results/ml_ready/flows_ml_ready.csv")
    print("\n💡 Next Step:")
    print("   python src/train_vpn_classifier.py --data results/ml_ready/flows_ml_ready.csv")

if __name__ == "__main__":
    main()
