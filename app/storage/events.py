import json
from pathlib import Path

from app.cfg import cfg
from app.schemas import Evt


class EventStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or cfg.event_file
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, evt: Evt) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evt.model_dump(mode="json"), ensure_ascii=False) + "\n")

    def list(self, resident_id: int | None = None, limit: int = 20) -> list[Evt]:
        rows: list[Evt] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = Evt.model_validate_json(line)
                if resident_id is None or item.resident_id == resident_id:
                    rows.append(item)
        return rows[-limit:]
