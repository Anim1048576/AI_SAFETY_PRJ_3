from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from app.cfg import cfg

try:
    import mediapipe as mp
except ImportError:  # pragma: no cover
    mp = None


@dataclass(slots=True)
class PoseHit:
    ok: bool = False
    vis: float = 0.0
    angle: float = 999.0
    wide: float = 0.0
    pts: list[tuple[float, float, float]] = field(default_factory=list)


class FallDet:
    def __init__(self) -> None:
        self.pose: Any | None = None
        self.flat_from: float | None = None
        self.armed = True

    def load(self) -> None:
        if mp is None:
            return
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def read(self, frame: np.ndarray) -> PoseHit:
        if self.pose is None:
            self.load()
        if self.pose is None:
            return PoseHit(ok=False)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out = self.pose.process(rgb)
        if not out.pose_landmarks:
            return PoseHit(ok=False)

        h, w, _ = frame.shape
        lms = out.pose_landmarks.landmark

        pts = [(lm.x * w, lm.y * h, lm.visibility) for lm in lms]

        ids = mp.solutions.pose.PoseLandmark
        ls = pts[ids.LEFT_SHOULDER.value]
        rs = pts[ids.RIGHT_SHOULDER.value]
        lh = pts[ids.LEFT_HIP.value]
        rh = pts[ids.RIGHT_HIP.value]
        nose = pts[ids.NOSE.value]

        vis = float(np.mean([ls[2], rs[2], lh[2], rh[2], nose[2]]))

        sx = (ls[0] + rs[0]) / 2.0
        sy = (ls[1] + rs[1]) / 2.0
        hx = (lh[0] + rh[0]) / 2.0
        hy = (lh[1] + rh[1]) / 2.0

        dx = hx - sx
        dy = hy - sy
        angle = abs(float(np.degrees(np.arctan2(dy, dx))))
        angle = min(angle, abs(180.0 - angle))

        xs = [p[0] for p in pts if p[2] > 0.2]
        ys = [p[1] for p in pts if p[2] > 0.2]
        bw = max(xs) - min(xs) if xs else 1.0
        bh = max(ys) - min(ys) if ys else 1.0
        wide = float(bw / max(bh, 1.0))

        return PoseHit(ok=True, vis=vis, angle=angle, wide=wide, pts=pts)

    def flat(self, hit: PoseHit) -> bool:
        if not hit.ok or hit.vis < cfg.min_vis:
            return False
        return hit.angle <= cfg.flat_deg and hit.wide >= cfg.wide_ratio

    def tick(self, hit: PoseHit, sec: float) -> dict[str, float] | None:
        if self.flat(hit):
            if self.flat_from is None:
                self.flat_from = sec
            hold = sec - self.flat_from
            if hold >= cfg.fall_hold_s and self.armed:
                self.armed = False
                return {
                    "torso_angle_deg": round(hit.angle, 3),
                    "flat_s": round(hold, 3),
                    "pose_conf": round(hit.vis, 3),
                    "wide_ratio": round(hit.wide, 3),
                    "num_persons": 1,
                }
            return None

        self.flat_from = None
        self.armed = True
        return None
