from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from app.cfg import cfg


class SnapStore:
    def __init__(self, base: Path | None = None) -> None:
        self.base = base or cfg.snap_dir
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, frame: np.ndarray, resident_id: int, kind: str, at: datetime) -> str:
        day = at.strftime("%Y-%m-%d")
        folder = self.base / day / f"resident_{resident_id}"
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{kind}_{at.strftime('%H%M%S')}.jpg"
        path = folder / name
        cv2.imwrite(str(path), frame)
        return str(path).replace("\\", "/")
