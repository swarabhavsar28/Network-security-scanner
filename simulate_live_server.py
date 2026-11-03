import urllib.request
import json
import time
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/ingest"

print("========================================")
print("🚀 Starting Nexus SIEM Live Agent...")
print(f"📡 Transmitting web logs to {API_URL}")
print("========================================\n")

normal_ips = [f"192.168.1.{i}" for i in range(10, 50)]
attacker_ip = "188.166.44.11"
brute_force_ip = "45.33.22.10"

try:
    while True:
        now = datetime.now().isoformat()
        
        # Normal traffic (80% of the time)
        if random.random() < 0.8:
            log = {
                "timestamp": now,
                "client_ip": random.choice(normal_ips),
                "method": "GET",
                "url": random.choice(["/index.html", "/about", "/contact", "/api/v1/status"]),
                "status_code": 200
            }
            print(f"[NORMAL]  {log['client_ip']} -> {log['url']}")
        
        # Anomalies (20% of the time)
        else:
            anomaly_type = random.choice(["sqli", "xss", "404"])
            if anomaly_type == "sqli":
                log = {
                    "timestamp": now,
                    "client_ip": attacker_ip,
                    "method": "POST",
                    "url": "/login?user=admin' OR 1=1--",
                    "status_code": 500
                }
                print(f"[ALERT]   SQLi attempt from {attacker_ip}!")
            elif anomaly_type == "xss":
                log = {
                    "timestamp": now,
                    "client_ip": attacker_ip,
                    "method": "GET",
                    "url": "/search?q=<script>alert(1)</script>",
                    "status_code": 200
                }
                print(f"[ALERT]   XSS payload from {attacker_ip}!")
            else:
                log = {
                    "timestamp": now,
                    "client_ip": brute_force_ip,
                    "method": "GET",
                    "url": f"/hidden_admin_dir_{random.randint(1,100)}.php",
                    "status_code": 404
                }
                print(f"[WARNING] 404 scan from {brute_force_ip}")
        
        try:
            req = urllib.request.Request(API_URL, data=json.dumps(log).encode('utf-8'), headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"❌ Failed to connect to SIEM: Is the FastAPI server running on port 8000?")
            
        time.sleep(random.uniform(0.5, 2.0))
        
except KeyboardInterrupt:
    print("\n🛑 Agent stopped.")
