from collections.abc import Callable
from typing import Any

import httpx

from app.cfg import cfg
from app.schemas import Evt, SleepRes


class Notifier:
    def __init__(self, post: Callable[..., Any] | None = None) -> None:
        self.post = post or httpx.post

    def sleep(self, resident_id: int) -> SleepRes:
        return SleepRes(
            resident_id=resident_id,
            start=cfg.quiet_start,
            end=cfg.quiet_end,
        )

    def send(self, evt: Evt) -> dict[str, Any]:
        if not cfg.api_url:
            return {"ok": False, "why": "api_url empty"}
        data = evt.model_dump(mode="json")
        return self.retry(data)

    def retry(self, data: dict[str, Any]) -> dict[str, Any]:
        last_err = ""
        for _ in range(cfg.retry_n + 1):
            try:
                res = self.post(cfg.api_url, json=data, timeout=cfg.api_timeout_s)
                if 200 <= res.status_code < 300:
                    return {"ok": True, "code": res.status_code}
                last_err = f"bad status: {res.status_code}"
            except Exception as e:  # pragma: no cover
                last_err = str(e)
        return {"ok": False, "why": last_err}
