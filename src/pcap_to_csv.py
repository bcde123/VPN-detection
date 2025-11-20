import pandas as pd
import os
from nfstream import NFStreamer

def process_pcap_folder(folder_path, label):
    flows = []
    if not os.path.exists(folder_path):
        print(f"Warning: Folder {folder_path} does not exist.")
        return pd.DataFrame()
        
    for file in os.listdir(folder_path):
        if file.endswith(".pcap") or file.endswith(".pcapng"):
            file_path = os.path.join(folder_path, file)
            print(f"Processing {file_path}...")
            try:
                # NFStreamer extracts flows from PCAP
                streamer = NFStreamer(source=file_path)
                for flow in streamer:
                    flows.append({
                        'src_ip': flow.src_ip,
                        'dst_ip': flow.dst_ip,
                        'src_port': flow.src_port,
                        'dst_port': flow.dst_port,
                        'protocol': flow.protocol,
                        'duration': flow.bidirectional_duration_ms / 1000.0, # Convert ms to seconds
                        'packet_count': flow.bidirectional_packets,
                        'byte_count': flow.bidirectional_bytes,
                        'label': label
                    })
            except Exception as e:
                print(f"Error processing {file}: {e}")
                
    return pd.DataFrame(flows)

def main():
    vpn_path = "data/VPN-PCAPS-01"
    non_vpn_path = "data/NonVPN-PCAPs-01"
    output_csv = "data/combined_flows.csv"
    
    print("Processing VPN PCAPs...")
    df_vpn = process_pcap_folder(vpn_path, label="VPN")
    
    print("Processing Non-VPN PCAPs...")
    df_non_vpn = process_pcap_folder(non_vpn_path, label="Non-VPN")
    
    if df_vpn.empty and df_non_vpn.empty:
        print("No flows extracted. Check if PCAP files exist in data/ directory.")
        return

    combined_df = pd.concat([df_vpn, df_non_vpn], ignore_index=True)
    
    print(f"Saving {len(combined_df)} flows to {output_csv}...")
    combined_df.to_csv(output_csv, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
