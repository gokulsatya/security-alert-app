from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Security Alert Management API")

# ---- The "shape" of an alert coming IN from the user ----
# Pydantic checks the incoming data matches these types automatically.
# We DON'T ask the user for id/created_at/updated_at — the server sets those.
class AlertIn(BaseModel):
    title: str
    description: str
    severity: str   # Low / Medium / High / Critical
    status: str     # Open / In Progress / Closed
    source: str     # Email / Endpoint / Firewall / Cloud / SIEM

# ---- Fake in-memory "database": just a Python list for today ----
# Day 2 replaces this with a real database.
alerts = []
next_id = 1   # we increment this to give each alert a unique id


# ---- GET /alerts : return ALL alerts ----
@app.get("/alerts")
def get_all_alerts():
    return alerts


# ---- GET /alerts/{id} : return ONE alert by its id ----
@app.get("/alerts/{alert_id}")
def get_one_alert(alert_id: int):
    for alert in alerts:
        if alert["id"] == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


# ---- POST /alerts : CREATE a new alert ----
@app.post("/alerts", status_code=201)   # 201 = "Created"
def create_alert(alert_in: AlertIn):
    global next_id
    now = datetime.now().isoformat()
    new_alert = {
        "id": next_id,
        "title": alert_in.title,
        "description": alert_in.description,
        "severity": alert_in.severity,
        "status": alert_in.status,
        "source": alert_in.source,
        "created_at": now,
        "updated_at": now,
    }
    alerts.append(new_alert)
    next_id += 1
    return new_alert


# ---- PUT /alerts/{id} : UPDATE an existing alert ----
@app.put("/alerts/{alert_id}")
def update_alert(alert_id: int, alert_in: AlertIn):
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["title"] = alert_in.title
            alert["description"] = alert_in.description
            alert["severity"] = alert_in.severity
            alert["status"] = alert_in.status
            alert["source"] = alert_in.source
            alert["updated_at"] = datetime.now().isoformat()
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


# ---- DELETE /alerts/{id} : remove an alert ----
@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int):
    for index, alert in enumerate(alerts):
        if alert["id"] == alert_id:
            alerts.pop(index)
            return {"message": "Alert deleted"}
    raise HTTPException(status_code=404, detail="Alert not found")