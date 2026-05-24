from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import csv
import io
import logging
import time
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal, Base
import models
from schemas import AlertIn, AlertOut

# This line tells SQLAlchemy to create the "alerts" table in alerts.db
# (if it doesn't already exist). This is what makes the .db file appear.
Base.metadata.create_all(bind=engine)

# ---- Logging setup ----
# Records each request to BOTH the terminal and a file (app.log).
# logging is Python's standard library — no install needed.
logging.basicConfig(
    level=logging.INFO,  # record INFO and above (INFO, WARNING, ERROR)
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),          # prints to the terminal
        logging.FileHandler("app.log"),   # also writes to app.log on disk
    ],
)
logger = logging.getLogger("security-alert-app")

app = FastAPI(title="Security Alert Management API")
# ---- Allow the React frontend (on a different address) to call this API ----
# The browser blocks cross-address requests unless the server opts in via CORS.
# We explicitly trust the React dev server's address.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # allow all request headers
)




# ---- Dependency: hand each endpoint a database session, then close it ----
def get_db():
    db = SessionLocal()
    try:
        yield db          # give the session to the endpoint
    finally:
        db.close()        # always close it, even if an error happened


# ---- GET /alerts : return ALL alerts ----
@app.get("/alerts", response_model=list[AlertOut])
def get_all_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).all()

# ---- GET /alerts/export : download ALL alerts as a CSV file ----
# NOTE: this MUST be defined ABOVE the "/alerts/{alert_id}" route below.
# FastAPI matches routes top-to-bottom; if {alert_id} came first it would
# try to read the word "export" as an id and fail.
@app.get("/alerts/export")
def export_alerts_csv(db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).all()

    # Write the CSV into an in-memory text buffer (not a file on disk).
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Header row — the column names.
    writer.writerow(
        ["id", "title", "description", "severity",
         "status", "source", "created_at", "updated_at"]
    )

    # One row per alert.
    for alert in alerts:
        writer.writerow([
            alert.id,
            alert.title,
            alert.description,
            alert.severity,
            alert.status,
            alert.source,
            alert.created_at,
            alert.updated_at,
        ])

    buffer.seek(0)  # rewind to the start so the response reads from the top

    # The Content-Disposition header tells the browser: download this,
    # don't display it, and name the file alerts.csv.
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=alerts.csv"},
    )

# ---- GET /alerts/{id} : return ONE alert by id ----
@app.get("/alerts/{alert_id}", response_model=AlertOut)
def get_one_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# ---- POST /alerts : CREATE a new alert ----
@app.post("/alerts", response_model=AlertOut, status_code=201)
def create_alert(alert_in: AlertIn, db: Session = Depends(get_db)):
    new_alert = models.Alert(
        title=alert_in.title,
        description=alert_in.description,
        severity=alert_in.severity.value,
        status=alert_in.status.value,
        source=alert_in.source.value,
    )
    db.add(new_alert)        # stage the new row
    db.commit()              # save it to the database
    db.refresh(new_alert)    # reload it so we get the id + timestamps
    return new_alert


# ---- PUT /alerts/{id} : UPDATE an existing alert ----
@app.put("/alerts/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, alert_in: AlertIn, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.title = alert_in.title
    alert.description = alert_in.description
    alert.severity = alert_in.severity.value
    alert.status = alert_in.status.value
    alert.source = alert_in.source.value

    db.commit()
    db.refresh(alert)
    return alert


# ---- DELETE /alerts/{id} : remove an alert ----
@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted"}