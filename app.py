from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
import io
import os
from analyzer import analyze_logs

app = FastAPI(title="Nexus SIEM")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory database for live log ingestion
LIVE_LOGS = []

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

# 1. Traditional CSV Upload Endpoint
@app.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")
    
    results = analyze_logs(df)
    if "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])
    return {"status": "success", "data": results}

# 2. Real-Time Log Ingestion Endpoint
@app.post("/api/ingest")
async def ingest_logs(request: Request):
    global LIVE_LOGS
    try:
        data = await request.json()
        if isinstance(data, list):
            LIVE_LOGS.extend(data)
        else:
            LIVE_LOGS.append(data)
            
        # Memory protection: Keep only the last 2000 events
        if len(LIVE_LOGS) > 2000:
            LIVE_LOGS = LIVE_LOGS[-2000:]
            
        return {"status": "success", "ingested": len(data) if isinstance(data, list) else 1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

# 3. Endpoint for Dashboard to Poll Live Data
@app.get("/api/live-data")
async def get_live_data():
    if not LIVE_LOGS:
        return {"status": "success", "data": {
            "stats": {"total_logs": 0, "total_anomalies": 0, "anomaly_breakdown": {}, "top_active_ips": {}, "log_type": "Awaiting Telemetry..."},
            "events": []
        }}
    
    df = pd.DataFrame(LIVE_LOGS)
    results = analyze_logs(df)
    
    if "error" in results:
         # If columns don't match exactly yet, just return empty state gracefully
         return {"status": "success", "data": {
            "stats": {"total_logs": len(df), "total_anomalies": 0, "anomaly_breakdown": {}, "top_active_ips": {}, "log_type": "Parsing Data..."},
            "events": []
        }}
         
    return {"status": "success", "data": results}

# 4. Utility to clear live memory
@app.delete("/api/live-data")
async def clear_live_data():
    global LIVE_LOGS
    LIVE_LOGS.clear()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
