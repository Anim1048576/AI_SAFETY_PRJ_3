from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Cfg(BaseSettings):
    app_name: str = "AI Smart Safety MVP"
    data_dir: Path = Path("data")
    snap_dir: Path = Path("data/snapshots")
    event_file: Path = Path("data/events.jsonl")

    sample_fps: float = 5.0
    flat_deg: float = 25.0
    fall_hold_s: float = 5.0
    min_vis: float = 0.45
    wide_ratio: float = 1.10

    motion_th: float = 0.0025
    still_s: float = 30.0
    mog2_history: int = 500
    mog2_var_th: float = 16.0

    api_url: str = ""
    api_timeout_s: float = 5.0
    retry_n: int = 2

    quiet_start: str = "23:00"
    quiet_end: str = "07:00"
    tz: str = "Asia/Seoul"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SAFE_",
        extra="ignore",
    )


cfg = Cfg()
cfg.data_dir.mkdir(parents=True, exist_ok=True)
cfg.snap_dir.mkdir(parents=True, exist_ok=True)
cfg.event_file.parent.mkdir(parents=True, exist_ok=True)
