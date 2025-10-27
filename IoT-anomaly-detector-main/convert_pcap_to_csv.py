import scapy.all as scapy
import pandas as pd
import os

# Path to your pcap files
pcap_dir = os.path.join("Dataset", "Profile trace")

files = [f for f in os.listdir(pcap_dir) if f.endswith(".pcap")]
all_data = []

for file in files:
    file_path = os.path.join(pcap_dir, file)
    print(f"Processing: {file}")
    try:
        packets = scapy.rdpcap(file_path)
        for p in packets:
            if "IP" in p:
                all_data.append({
                    "src": p["IP"].src,
                    "dst": p["IP"].dst,
                    "proto": p["IP"].proto,
                    "len": len(p),
                    "label": "unknown"
                })
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Save to CSV in the main folder
csv_path = "pptp.csv"
df.to_csv(csv_path, index=False)
print(f"Successfully created {csv_path} with {len(df)} rows.")
