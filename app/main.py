import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException

from app.cfg import cfg
from app.schemas import AnalyzeRes, Evt, HealthRes
from app.service import Analyzer
from app.storage.events import EventStore

log = logging.getLogger(__name__)

app = FastAPI(title=cfg.app_name, version="0.1.0")


@app.get("/health", response_model=HealthRes)
def health() -> HealthRes:
    return HealthRes(app=cfg.app_name)


@app.post("/analyze/video", response_model=AnalyzeRes)
async def analyze_video(
    resident_id: int = Form(...),
    video: UploadFile = File(...),
    notify: bool = Form(False),
) -> AnalyzeRes:
    suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"
    tmp_path = ""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            while True:
                chunk = await video.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)

        analyzer = Analyzer()
        return analyzer.run(
            video_path=tmp_path,
            resident_id=resident_id,
            video_name=video.filename or Path(tmp_path).name,
            notify=notify,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        log.exception("analyze_video failed")
        raise HTTPException(status_code=500, detail=f"analyze failed: {e}")

    finally:
        await video.close()
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/events/{resident_id}", response_model=list[Evt])
def list_events(resident_id: int, limit: int = 20) -> list[Evt]:
    return EventStore().list(resident_id=resident_id, limit=limit)
