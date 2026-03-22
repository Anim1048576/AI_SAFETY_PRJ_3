from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import cv2
import numpy as np


@dataclass(slots=True)
class FrameRow:
    idx: int
    sec: float
    frame: np.ndarray


class FrameSrc:
    def __init__(self, path: str | Path, sample_fps: float) -> None:
        self.path = str(path)
        self.sample_fps = sample_fps

    def rows(self) -> Generator[FrameRow, None, None]:
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            raise ValueError(f"video open failed: {self.path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps))) if self.sample_fps > 0 else 1

        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                yield FrameRow(idx=idx, sec=idx / fps, frame=frame)
            idx += 1

        cap.release()
