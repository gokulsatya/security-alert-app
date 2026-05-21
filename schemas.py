from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum


# An Enum is a fixed set of allowed values. By defining these,
# we force severity/status/source to be EXACTLY one of these strings.
# Anything else (like lowercase "low") is automatically rejected.
class Severity(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class Status(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    closed = "Closed"


class Source(str, Enum):
    email = "Email"
    endpoint = "Endpoint"
    firewall = "Firewall"
    cloud = "Cloud"
    siem = "SIEM"


# ---- The rules for data coming IN (create/update) ----
class AlertIn(BaseModel):
    title: str
    description: str
    severity: Severity   # must match the Severity enum above
    status: Status       # must match the Status enum above
    source: Source       # must match the Source enum above

    # This runs automatically for the "title" field.
    # We strip surrounding spaces and reject if nothing is left.
    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    # This runs automatically for "description".
    # Reject if it's shorter than 10 characters (after trimming).
    @field_validator("description")
    @classmethod
    def description_min_length(cls, value):
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Description must be at least 10 characters")
        return cleaned


# ---- The shape of data going OUT (what the API returns) ----
# This includes the server-set fields the user never sends.
class AlertOut(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    # This lets Pydantic read data straight from a SQLAlchemy row object.
    class Config:
        from_attributes = True