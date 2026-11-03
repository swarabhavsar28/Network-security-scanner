import pandas as pd
import re

# --- Network Rules ---
BLACKLISTED_IPS = {"192.168.1.100", "10.0.0.55"}
COMMON_PORTS = {80, 443, 22, 21, 53}
NETWORK_SPIKE_THRESHOLD = 50

# --- Web Rules ---
SQLI_PATTERN = re.compile(r"(UNION SELECT|' OR 1=1|--|; DROP TABLE)", re.IGNORECASE)
XSS_PATTERN = re.compile(r"(<script>|javascript:|onerror=)", re.IGNORECASE)
DIR_BRUTE_THRESHOLD = 20

# --- Auth Rules ---
BRUTE_FORCE_THRESHOLD = 5
SENSITIVE_USERS = {"root", "admin", "administrator", "sysadmin"}

def analyze_logs(df: pd.DataFrame) -> dict:
    columns = set(df.columns)
    
    # Auto-detect log type
    if {'source_ip', 'destination_port'}.issubset(columns):
        return analyze_network(df)
    elif {'client_ip', 'url', 'status_code'}.issubset(columns):
        return analyze_web(df)
    elif {'user', 'ip_address', 'action', 'status'}.issubset(columns):
        return analyze_auth(df)
    else:
        return {"error": f"Unknown log format. Detected columns: {list(columns)}"}

def analyze_network(df: pd.DataFrame) -> dict:
    flagged_events = []
    
    # 1. Unusual Ports
    unusual = df[~df['destination_port'].isin(COMMON_PORTS)]
    for _, row in unusual.iterrows():
        flagged_events.append(create_event(row, row['source_ip'], "Unusual Port", f"Port {row['destination_port']} used"))

    # 2. Blacklisted
    blacklisted = df[df['source_ip'].isin(BLACKLISTED_IPS) | df['destination_ip'].isin(BLACKLISTED_IPS)]
    for _, row in blacklisted.iterrows():
        ip = row['source_ip'] if row['source_ip'] in BLACKLISTED_IPS else row['destination_ip']
        flagged_events.append(create_event(row, row['source_ip'], "Blacklisted IP", f"Traffic with known bad IP: {ip}"))

    # 3. Spikes
    counts = df['source_ip'].value_counts()
    for ip in counts[counts > NETWORK_SPIKE_THRESHOLD].index:
        last_time = df[df['source_ip'] == ip]['timestamp'].max()
        flagged_events.append(create_event({'timestamp': last_time, 'destination_port': 'N/A', 'destination_ip': 'Multiple'}, ip, "Traffic Spike (DDoS)", f"{counts[ip]} requests detected"))

    return compile_results(df, flagged_events, 'source_ip', 'Network Traffic')

def analyze_web(df: pd.DataFrame) -> dict:
    flagged_events = []
    
    for _, row in df.iterrows():
        url = str(row.get('url', ''))
        # 1. SQLi
        if SQLI_PATTERN.search(url):
            flagged_events.append(create_event(row, row['client_ip'], "SQL Injection Attempt", f"Payload detected in URL: {url}"))
        # 2. XSS
        elif XSS_PATTERN.search(url):
            flagged_events.append(create_event(row, row['client_ip'], "XSS Attempt", f"Script payload detected in URL: {url}"))
            
    # 3. Directory Brute Forcing (High 404s)
    if 'status_code' in df.columns:
        errors = df[df['status_code'] == 404]
        counts = errors['client_ip'].value_counts()
        for ip in counts[counts > DIR_BRUTE_THRESHOLD].index:
            last_time = errors[errors['client_ip'] == ip]['timestamp'].max()
            flagged_events.append(create_event({'timestamp': last_time, 'destination_port': '80/443', 'destination_ip': 'Web Server'}, ip, "Dir Brute Force", f"{counts[ip]} 404 errors detected"))

    return compile_results(df, flagged_events, 'client_ip', 'Web Server Logs')

def analyze_auth(df: pd.DataFrame) -> dict:
    flagged_events = []
    
    # 1. High-value target
    for _, row in df[df['user'].isin(SENSITIVE_USERS)].iterrows():
        if row.get('status') == 'FAILED':
            flagged_events.append(create_event(row, row['ip_address'], "Admin Login Attempt", f"Failed attempt for sensitive user: {row['user']}"))

    # 2. Brute force (multiple failures)
    failed = df[df['status'] == 'FAILED']
    counts = failed['ip_address'].value_counts()
    for ip in counts[counts > BRUTE_FORCE_THRESHOLD].index:
        last_time = failed[failed['ip_address'] == ip]['timestamp'].max()
        flagged_events.append(create_event({'timestamp': last_time, 'destination_port': 'Auth', 'destination_ip': 'Auth Server'}, ip, "Brute Force Attack", f"{counts[ip]} failed logins detected"))

    return compile_results(df, flagged_events, 'ip_address', 'Authentication Logs')

def create_event(row, source, reason, details):
    return {
        "timestamp": str(row.get('timestamp', '')),
        "source_ip": str(source),
        "destination_ip": str(row.get('destination_ip', 'N/A')),
        "destination_port": str(row.get('destination_port', 'N/A')),
        "reason": reason,
        "details": details
    }

def compile_results(df, flagged_events, ip_column, log_type):
    flagged_events.sort(key=lambda x: x.get('timestamp', ''))
    
    breakdown = {}
    for event in flagged_events:
        breakdown[event['reason']] = breakdown.get(event['reason'], 0) + 1
        
    top_ips = {str(k): int(v) for k, v in df[ip_column].value_counts().head(5).items()}

    return {
        "stats": {
            "total_logs": len(df),
            "total_anomalies": len(flagged_events),
            "anomaly_breakdown": breakdown,
            "top_active_ips": top_ips,
            "log_type": log_type
        },
        "events": flagged_events
    }
