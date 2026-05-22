from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal, Base
import models
from schemas import AlertIn, AlertOut

# This line tells SQLAlchemy to create the "alerts" table in alerts.db
# (if it doesn't already exist). This is what makes the .db file appear.
Base.metadata.create_all(bind=engine)

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