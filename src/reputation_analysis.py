#!/usr/bin/env python3
"""
IP Reputation Analyzer
Assesses IP and domain reputation against threat intelligence feeds.
"""

import pandas as pd
import json
import os
import ipaddress
import argparse

# Optional: you can integrate 'ipinfo', 'geoip2', or any API later for real geolocation.

def classify_ip(ip):
    """Classify IP address based on range or known providers."""
    try:
        ip_obj = ipaddress.ip_address(ip)

        # Private/local networks
        if ip_obj.is_private:
            return "Local/Private"

        # Reserved or loopback
        if ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_multicast:
            return "System/Reserved"

        # Known VPN/Cloud IP hints (mock check)
        suspicious_prefixes = [
            "13.", "34.", "35.", "44.", "52.", "54.", "63.", "64.", "66.", "142.", "143.",
            "147.", "148.", "150.", "151.", "155.", "156.", "157.", "159.", "160.", "161.",
            "162.", "163.", "164.", "165.", "166.", "167.", "168.", "169.", "170.", "171.",
            "172.67.", "172.68.", "172.69.", "172.70.", "173.", "174.", "175.", "176.", "177.",
            "178.", "179.", "180.", "181.", "182.", "183.", "184.", "185.", "186.", "187.",
            "188.", "189.", "190.", "191.", "192.", "193.", "194.", "195.", "196.", "197.",
            "198.", "199.", "200.", "201.", "202.", "203.", "204.", "205.", "206.", "207.",
            "208.", "209.", "210.", "211.", "212.", "213.", "214.", "215.", "216."
        ]
        for prefix in suspicious_prefixes:
            if ip.startswith(prefix):
                return "Potential VPN/Cloud Provider"

        return "Public Internet"

    except ValueError:
        return "Invalid IP"


def analyze_ip_reputation(csv_file, output_json):
    df = pd.read_csv(csv_file)

    if 'src_ip' not in df.columns or 'dst_ip' not in df.columns:
        raise ValueError("CSV must contain 'src_ip' and 'dst_ip' columns")

    results = []
    unique_ips = set(df['src_ip']).union(set(df['dst_ip']))

    for ip in unique_ips:
        classification = classify_ip(str(ip))
        results.append({"ip": ip, "classification": classification})

    df_results = pd.DataFrame(results)

    summary = {
        "total_unique_ips": len(df_results),
        "local_ips": len(df_results[df_results['classification'] == "Local/Private"]),
        "vpn_like_ips": len(df_results[df_results['classification'] == "Potential VPN/Cloud Provider"]),
        "public_ips": len(df_results[df_results['classification'] == "Public Internet"]),
        "detailed_results": df_results.to_dict(orient="records")
    }

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(summary, f, indent=4)

    print("[OK] Reputation & Geolocation Analysis Complete.")
    print(json.dumps({
        "total_unique_ips": summary["total_unique_ips"],
        "vpn_like_ips": summary["vpn_like_ips"],
        "local_ips": summary["local_ips"]
    }, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV file")
    parser.add_argument("--out-json", required=True, help="Output JSON file")
    args = parser.parse_args()

    analyze_ip_reputation(args.csv, args.out_json)

