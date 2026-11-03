import csv
import random
from datetime import datetime, timedelta

def write_csv(filename, data):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'source_ip', 'destination_ip', 'destination_port', 'bytes_transferred'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Created {filename}")

def generate_clean_traffic():
    data = []
    start_time = datetime.now()
    common_ports = [80, 443]
    for i in range(200):
        data.append({
            'timestamp': (start_time + timedelta(seconds=i*2)).isoformat(),
            'source_ip': f"192.168.1.{random.randint(10, 50)}",
            'destination_ip': f"{random.randint(1, 200)}.{random.randint(1, 255)}.10.10",
            'destination_port': random.choice(common_ports),
            'bytes_transferred': random.randint(500, 5000)
        })
    write_csv('test_case_1_clean_traffic.csv', data)

def generate_ddos_attack():
    data = []
    start_time = datetime.now()
    # 20 normal logs
    for i in range(20):
        data.append({
            'timestamp': (start_time + timedelta(seconds=i)).isoformat(),
            'source_ip': f"192.168.1.{random.randint(10, 50)}",
            'destination_ip': "10.0.0.1",
            'destination_port': 443,
            'bytes_transferred': random.randint(500, 5000)
        })
    # DDoS spike from one IP
    attacker_ip = "192.168.1.199"
    for i in range(100):
        data.append({
            'timestamp': (start_time + timedelta(seconds=20, milliseconds=i*10)).isoformat(),
            'source_ip': attacker_ip,
            'destination_ip': "10.0.0.1",
            'destination_port': 80,
            'bytes_transferred': random.randint(100, 200)
        })
    write_csv('test_case_2_ddos_attack.csv', data)

def generate_malware_beaconing():
    data = []
    start_time = datetime.now()
    blacklisted = "10.0.0.55" # From our analyzer.py
    for i in range(50):
        # Normal
        data.append({
            'timestamp': (start_time + timedelta(seconds=i*5)).isoformat(),
            'source_ip': "192.168.1.25",
            'destination_ip': "8.8.8.8",
            'destination_port': 443,
            'bytes_transferred': random.randint(500, 1000)
        })
        # Malware pinging unusual port and blacklisted IP
        if i % 10 == 0:
            data.append({
                'timestamp': (start_time + timedelta(seconds=i*5+1)).isoformat(),
                'source_ip': "192.168.1.25",
                'destination_ip': blacklisted,
                'destination_port': 6667, # IRC port commonly used by botnets
                'bytes_transferred': 55
            })
    write_csv('test_case_3_malware_beaconing.csv', data)

if __name__ == "__main__":
    generate_clean_traffic()
    generate_ddos_attack()
    generate_malware_beaconing()
