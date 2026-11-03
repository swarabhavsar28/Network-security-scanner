import csv
import random
from datetime import datetime, timedelta

def write_csv(filename, data, fieldnames):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Created {filename}")

def generate_web_logs():
    data = []
    start_time = datetime.now()
    for i in range(150):
        url = "/index.html"
        client = f"192.168.1.{random.randint(10, 50)}"
        status = 200
        
        # SQL Injection
        if i == 50:
            url = "/login?user=admin' OR 1=1--"
            client = "10.0.0.99"
        # XSS
        elif i == 100:
            url = "/search?q=<script>alert(1)</script>"
            client = "10.0.0.100"
            
        data.append({
            'timestamp': (start_time + timedelta(seconds=i*2)).isoformat(),
            'client_ip': client,
            'method': "GET",
            'url': url,
            'status_code': status
        })
        
    # Dir brute force
    brute_ip = "45.22.19.11"
    for i in range(25):
        data.append({
            'timestamp': (start_time + timedelta(seconds=300+i)).isoformat(),
            'client_ip': brute_ip,
            'method': "GET",
            'url': f"/hidden_dir_{i}.php",
            'status_code': 404
        })
        
    write_csv('test_case_4_web_attacks.csv', data, ['timestamp', 'client_ip', 'method', 'url', 'status_code'])

def generate_auth_logs():
    data = []
    start_time = datetime.now()
    for i in range(50):
        data.append({
            'timestamp': (start_time + timedelta(minutes=i*10)).isoformat(),
            'user': f"user{random.randint(1, 10)}",
            'ip_address': f"192.168.1.{random.randint(10, 50)}",
            'action': "login",
            'status': "SUCCESS"
        })
        
    # Admin failure
    data.append({
        'timestamp': (start_time + timedelta(minutes=55)).isoformat(),
        'user': "root",
        'ip_address': "10.0.0.66",
        'action': "login",
        'status': "FAILED"
    })
    
    # Brute Force
    brute_ip = "188.166.22.11"
    for i in range(10):
        data.append({
            'timestamp': (start_time + timedelta(minutes=60, seconds=i*5)).isoformat(),
            'user': "admin",
            'ip_address': brute_ip,
            'action': "login",
            'status': "FAILED"
        })
        
    write_csv('test_case_5_auth_attacks.csv', data, ['timestamp', 'user', 'ip_address', 'action', 'status'])

if __name__ == "__main__":
    generate_web_logs()
    generate_auth_logs()
