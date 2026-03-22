from datetime import datetime
from zoneinfo import ZoneInfo

from app.cfg import cfg



def now_local() -> datetime:
    return datetime.now(ZoneInfo(cfg.tz))
