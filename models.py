from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


# This class describes ONE row in the "alerts" table.
# SQLAlchemy reads it and builds a matching table in alerts.db.
class Alert(Base):
    __tablename__ = "alerts"   # the table will be named "alerts"

    # Each Column(...) below becomes a column in the database table.
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False)   # Low / Medium / High / Critical
    status = Column(String, nullable=False)      # Open / In Progress / Closed
    source = Column(String, nullable=False)      # Email / Endpoint / Firewall / Cloud / SIEM

    # The server fills these in automatically — the user never sends them.
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)