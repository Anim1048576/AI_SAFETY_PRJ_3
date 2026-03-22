from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvtType(str, Enum):
    FALL = "FALL"
    INACTIVE = "INACTIVE"


class EvtState(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CLOSED = "CLOSED"


class Evt(BaseModel):
    id: str
    resident_id: int
    event_type: EvtType
    status: EvtState = EvtState.PENDING
    detected_at: datetime
    snapshot_path: str
    description: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)


class AnalyzeRes(BaseModel):
    resident_id: int
    video_name: str
    events: list[Evt] = Field(default_factory=list)


class HealthRes(BaseModel):
    ok: bool = True
    app: str


class SleepRes(BaseModel):
    resident_id: int
    start: str
    end: str
