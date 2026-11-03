import csv
import random
from datetime import datetime, timedelta

def generate_sample_data(filename="sample_network_logs.csv", num_rows=1000):
    start_time = datetime.now()
    
    # Common ports
    common_ports = [80, 443, 22, 53]
    
    # Regular IPs
    regular_ips = [f"192.168.1.{i}" for i in range(10, 50)]
    
    # External IPs
    external_ips = [f"8.8.8.8", "1.1.1.1", "142.250.190.46"]
    
    # Known blacklisted (from our analyzer)
    blacklisted = ["192.168.1.100", "10.0.0.55"]
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'source_ip', 'destination_ip', 'destination_port', 'bytes_transferred']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for i in range(num_rows):
            # Normal traffic mostly
            src = random.choice(regular_ips)
            dst = random.choice(external_ips + regular_ips)
            port = random.choice(common_ports)
            
            # Inject some anomalies
            if i % 100 == 0:
                # Unusual port
                port = 6667
            elif i % 150 == 0:
                # Blacklisted IP communication
                src = random.choice(blacklisted)
            
            # Simulate a traffic spike for one specific IP
            if i > 800 and i < 860:
                src = "192.168.1.99"
                
            writer.writerow({
                'timestamp': (start_time + timedelta(seconds=i)).isoformat(),
                'source_ip': src,
                'destination_ip': dst,
                'destination_port': port,
                'bytes_transferred': random.randint(100, 10000)
            })
            
    print(f"Generated {filename} with {num_rows} records.")

if __name__ == "__main__":
    generate_sample_data()
