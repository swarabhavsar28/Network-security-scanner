# 🛡️ Nexus SIEM

> **A full-stack, real-time Security Information and Event Management (SIEM) dashboard** built with FastAPI and Python on the backend, and a responsive SPA frontend. Automatically detects threats across Network, Web, and Authentication logs.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Multi-Source Ingestion** | Auto-detects log type (Network, Web Server, Auth) from CSV columns |
| **Threat Detection** | SQL Injection, XSS, DDoS Spikes, Brute Force, Blacklisted IPs, Dir Scanning |
| **Live Monitoring** | Real-time API ingestion endpoint — push logs from any server |
| **Interactive Dashboard** | Charts, stat cards, risk scoring — all update dynamically |
| **Full SPA Navigation** | Dashboard, Incidents, Raw Logs, Data Sources, Settings |
| **Event Filtering** | Filter incidents by severity (Critical / Warning / Info) |
| **Search** | Global search + per-view log search |

---

## 🖥️ Tech Stack

```
Backend   →  Python 3.10+  •  FastAPI  •  Pandas  •  Uvicorn
Frontend  →  HTML5  •  Tailwind CSS  •  Chart.js  •  Vanilla JS
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/you/nexus-siem.git
cd nexus-siem
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Open your browser → **[http://localhost:8000](http://localhost:8000)**

---

## 📂 Project Structure

```
nexus-siem/
├── app.py                      # FastAPI server + API endpoints
├── analyzer.py                 # Core detection engine (rule-based)
├── requirements.txt
├── static/
│   ├── index.html              # Full SPA frontend
│   ├── script.js               # Navigation, charts, live mode
│   └── style.css               # Dark theme styles
│
└── test cases/
    ├── test_case_1_clean_traffic.csv      # Normal network baseline
    ├── test_case_2_ddos_attack.csv        # DDoS spike simulation
    ├── test_case_3_malware_beaconing.csv  # Blacklisted IP + unusual ports
    ├── test_case_4_web_attacks.csv        # SQLi + XSS + Dir brute force
    ├── test_case_5_auth_attacks.csv       # Brute force + admin targeting
    ├── generate_sample.py                 # Network log generator
    ├── generate_test_cases.py             # All test case generator
    ├── generate_other_logs.py             # Web + auth log generator
    └── simulate_live_server.py            # Live agent simulator
```

---

## 🧪 Testing with Sample Data

Generate all test CSVs at once:

```bash
python generate_sample.py
python generate_test_cases.py
python generate_other_logs.py
```

Then upload them via the dashboard **Ingest** button.

### What each file triggers:

| File | Threats Detected |
|---|---|
| `test_case_1_clean_traffic.csv` | ✅ All clear |
| `test_case_2_ddos_attack.csv` | 🔴 Traffic Spike (DDoS) |
| `test_case_3_malware_beaconing.csv` | 🔴 Blacklisted IP + 🟣 Unusual Port |
| `test_case_4_web_attacks.csv` | 🔴 SQL Injection + 🔴 XSS + 🟡 Dir Brute Force |
| `test_case_5_auth_attacks.csv` | 🟡 Brute Force Attack + 🟣 Admin Login Attempt |

---

## 📡 Live Ingestion API

The SIEM exposes a real-time ingestion REST API. Push logs from any server directly into the dashboard.

### 1. Enable Live Mode

Click the **Live Mode** button in the dashboard header to start polling.

### 2. Push a log event

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-09-19T04:00:00",
    "client_ip": "1.2.3.4",
    "method": "POST",
    "url": "/login?user=admin'"'"' OR 1=1--",
    "status_code": 500
  }'
```

### 3. Simulate a live server attack

Open a second terminal and run:

```bash
python simulate_live_server.py
```

The script will continuously generate realistic web traffic (both normal and malicious) and push it to your dashboard in real-time.

---

## 🔍 Detection Rules

### Network Traffic
| Rule | Trigger |
|---|---|
| **Unusual Port** | Destination port not in `{80, 443, 22, 21, 53}` |
| **Blacklisted IP** | Source or destination matches known bad IP list |
| **Traffic Spike (DDoS)** | Single source IP exceeds **50 requests** |

### Web Server Logs
| Rule | Trigger |
|---|---|
| **SQL Injection** | URL contains `UNION SELECT`, `' OR 1=1`, `--`, `; DROP TABLE` |
| **XSS Attempt** | URL contains `<script>`, `javascript:`, `onerror=` |
| **Dir Brute Force** | Single IP generates > **20 HTTP 404** responses |

### Authentication Logs
| Rule | Trigger |
|---|---|
| **Brute Force Attack** | Single IP has > **5 failed** login attempts |
| **Admin Login Attempt** | Failed login for users `root`, `admin`, `administrator`, `sysadmin` |

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the SPA dashboard |
| `POST` | `/upload` | Upload a CSV file for batch analysis |
| `POST` | `/api/ingest` | Push a single or batch JSON log event |
| `GET` | `/api/live-data` | Get analyzed results of all live-ingested logs |
| `DELETE` | `/api/live-data` | Clear the live log buffer |

---

## 🗺️ Dashboard Navigation

| View | Description |
|---|---|
| **Dashboard** | Overview: stats, charts, recent events |
| **Incidents** | Filterable full list of all anomalies (Critical/Warning/Info) |
| **Raw Logs** | Searchable, unfiltered event stream |
| **Data Sources** | Log format specs + live API integration guide |
| **Settings** | Detection thresholds, blacklist, and allowed ports |

---

## 📋 Resume Description

> **Nexus SIEM** — Full-Stack Security Dashboard (Python / FastAPI / JavaScript)
>
> Built a real-time Security Information and Event Management (SIEM) system capable of ingesting and analyzing network traffic, web server, and authentication logs. Implemented a rule-based threat detection engine in Python (Pandas) that identifies SQL Injection, XSS, DDoS attacks, brute-force attempts, and blacklisted IP communication. Designed a responsive single-page application (SPA) frontend with live API polling (2s refresh), interactive Chart.js visualizations, multi-view navigation, and dynamic event filtering. Exposed a REST ingestion endpoint allowing any web server to push logs in real-time.

---

## ⚡ Future Roadmap

- [ ] ML-based anomaly detection (Isolation Forest)
- [ ] Email / Webhook alert notifications
- [ ] PostgreSQL / TimescaleDB for persistent log storage
- [ ] User authentication & role-based access
- [ ] GeoIP threat mapping (world map visualization)
- [ ] Docker + docker-compose deployment

---

<p align="center">Built with ❤️ using FastAPI + Pandas + Chart.js</p>
