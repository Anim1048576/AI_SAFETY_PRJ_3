from pathlib import Path
from uuid import uuid4

from app.cfg import cfg
from app.detectors.fall import FallDet
from app.detectors.inactive import InactiveDet
from app.notifier import Notifier
from app.schemas import AnalyzeRes, Evt, EvtType
from app.storage.events import EventStore
from app.storage.snaps import SnapStore
from app.utils.time import now_local
from app.utils.video import FrameSrc


class Analyzer:
    def __init__(self) -> None:
        self.fall = FallDet()
        self.inactive = InactiveDet()
        self.snaps = SnapStore()
        self.events = EventStore()
        self.note = Notifier()
        self.cool_until = 0.0

    def run(self, video_path: str | Path, resident_id: int, video_name: str, notify: bool = False) -> AnalyzeRes:
        res = AnalyzeRes(resident_id=resident_id, video_name=video_name, events=[])
        src = FrameSrc(video_path, cfg.sample_fps)

        for row in src.rows():
            hit = self.fall.read(row.frame)

            fall_metrics = self.fall.tick(hit, row.sec)
            if fall_metrics:
                fall_metrics["video_sec"] = round(row.sec, 3)
                evt = self._make_evt(row.frame, resident_id, EvtType.FALL, "horizontal posture sustained", fall_metrics)
                res.events.append(evt)
                self.events.add(evt)
                if notify:
                    self.note.send(evt)
                self.inactive.reset()
                self.cool_until = row.sec + 10.0
                continue

            if row.sec < self.cool_until:
                continue

            inactive_metrics = self.inactive.tick(row.frame, row.sec, hit.ok)
            if inactive_metrics:
                inactive_metrics["video_sec"] = round(row.sec, 3)
                evt = self._make_evt(row.frame, resident_id, EvtType.INACTIVE, "long period without motion", inactive_metrics)
                res.events.append(evt)
                self.events.add(evt)
                if notify:
                    self.note.send(evt)

        return res

    def _make_evt(self, frame, resident_id: int, kind: EvtType, desc: str, metrics: dict) -> Evt:
        at = now_local()
        path = self.snaps.save(frame, resident_id, kind.value, at)
        payload = dict(metrics)
        return Evt(
            id=uuid4().hex[:12],
            resident_id=resident_id,
            event_type=kind,
            detected_at=at,
            snapshot_path=path,
            description=desc,
            metrics=payload,
        )
