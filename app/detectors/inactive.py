from dataclasses import dataclass

import cv2
import numpy as np

from app.cfg import cfg


@dataclass(slots=True)
class MotionHit:
    score: float
    seen: bool


class InactiveDet:
    def __init__(self) -> None:
        self.bg = cv2.createBackgroundSubtractorMOG2(
            history=cfg.mog2_history,
            varThreshold=cfg.mog2_var_th,
            detectShadows=True,
        )
        self.still_from: float | None = None
        self.armed = True
        self.day_sum = 0.0
        self.day_frames = 0

    def load(self) -> None:
        return

    def motion(self, frame: np.ndarray) -> float:
        mask = self.bg.apply(frame)
        mask = np.where(mask == 255, 255, 0).astype(np.uint8)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        score = float(np.count_nonzero(mask == 255) / mask.size)
        self.day_sum += score
        self.day_frames += 1
        return score

    def day_score(self) -> float:
        if self.day_frames == 0:
            return 0.0
        return self.day_sum / self.day_frames

    def tick(self, frame: np.ndarray, sec: float, seen: bool) -> dict[str, float] | None:
        score = self.motion(frame)
        if not seen:
            self.reset()
            return None

        if score < cfg.motion_th:
            if self.still_from is None:
                self.still_from = sec
            hold = sec - self.still_from
            if hold >= cfg.still_s and self.armed:
                self.armed = False
                return {
                    "motion_score": round(score, 6),
                    "still_s": round(hold, 3),
                    "day_motion": round(self.day_score(), 6),
                    "num_persons": 1,
                }
            return None

        self.still_from = None
        self.armed = True
        return None

    def reset(self) -> None:
        self.still_from = None
        self.armed = True
