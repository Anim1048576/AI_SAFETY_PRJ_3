# AI 스마트 생활안전 서비스 MVP - Python 프로젝트

FastAPI 중심으로 다시 짠 Python MVP입니다.
핵심 흐름은 아래 4개로 고정했습니다.

- 비디오 입력
- 낙상(FALL) 감지
- 장시간 무응답(INACTIVE) 감지
- 스냅샷 저장 + JSON 반환 + 선택적 서버 전송

## 왜 이렇게 짰는가

업로드된 PRD/계획서 기준으로 Python 범위는 **감지 → 이벤트 생성 → 스냅샷 저장 → 결과(JSON) 반환**에 집중하고,
상태 변경 같은 관제 로직은 Spring Boot 쪽으로 넘기는 구조가 맞습니다.
그래서 프로젝트도 그 흐름만 바로 데모 가능한 형태로 잘랐습니다.

## 폴더 구조

```text
ai_safety_vibe/
├─ app/
│  ├─ main.py              # FastAPI 엔트리
│  ├─ cli.py               # CLI 실행기
│  ├─ cfg.py               # 환경설정
│  ├─ schemas.py           # 응답/이벤트 모델
│  ├─ service.py           # 분석 흐름 총괄
│  ├─ notifier.py          # 선택적 Spring 전송
│  ├─ detectors/
│  │  ├─ fall.py           # FA-001
│  │  ├─ inactive.py       # FA-002
│  │  └─ fight.py          # FA-003 자리만 확보, 미사용
│  ├─ storage/
│  │  ├─ events.py         # events.jsonl 저장
│  │  └─ snaps.py          # 이벤트 스냅샷 저장
│  └─ utils/
│     ├─ time.py
│     └─ video.py
├─ docs/
│  └─ method_map.md
├─ .env.example
└─ requirements.txt
```

## 공개 이름 원칙

바깥에서 자주 쓰는 이름은 짧게 맞췄습니다.

- API: `/health`, `/analyze/video`, `/events/{resident_id}`
- CLI 옵션: `--resident`, `--video`, `--notify`
- 공개 메서드: `load()`, `read()`, `flat()`, `tick()`, `motion()`, `send()`, `retry()`

## 설치

```bash
py -3.11 -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## 실행

### 1) API 서버

```bash
uvicorn app.main:app --reload
```

문서 주소:

- Swagger UI: `http://127.0.0.1:8000/docs`

### 2) CLI 분석

```bash
python -m app.cli --resident 1 --video sample.mp4
```

## API 예시

```bash
curl -X POST "http://127.0.0.1:8000/analyze/video" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "resident_id=1" \
  -F "video=@sample.mp4;type=video/mp4" \
  -F "notify=false"
```

## 응답 예시

```json
{
  "resident_id": 1,
  "video_name": "sample.mp4",
  "events": [
    {
      "id": "0b7fc2b6f818",
      "resident_id": 1,
      "event_type": "FALL",
      "status": "PENDING",
      "detected_at": "2026-03-22T12:34:56+09:00",
      "snapshot_path": "data/snapshots/2026-03-22/resident_1/FALL_123456.jpg",
      "description": "horizontal posture sustained",
      "metrics": {
        "torso_angle_deg": 11.2,
        "flat_s": 6.1,
        "pose_conf": 0.84,
        "wide_ratio": 1.42,
        "num_persons": 1,
        "video_sec": 0.0
      }
    }
  ]
}
```

## 감지 규칙

### FALL

- MediaPipe Pose로 랜드마크 추출
- 몸통 각도가 수평에 가까운지 확인
- 사람 외곽이 가로로 넓은지 확인
- 그 상태가 `SAFE_FALL_HOLD_S` 이상 유지되면 이벤트 발생

### INACTIVE

- OpenCV MOG2로 foreground mask 생성
- 움직임 픽셀 비율을 `motion_score`로 계산
- 사람이 화면에 있는 상태에서
- 움직임이 `SAFE_MOTION_TH` 미만인 시간이 `SAFE_STILL_S` 이상이면 이벤트 발생

## 저장 위치

- 이벤트 로그: `data/events.jsonl`
- 스냅샷: `data/snapshots/YYYY-MM-DD/resident_{id}/...jpg`

## Spring Boot 연동

`.env`에 아래 값만 넣으면 `notify=true`일 때 전송을 시도합니다.

```env
SAFE_API_URL=http://127.0.0.1:8080/internal/detection/events
```

## 주의

- `fight.py`는 첨부 이미지의 FA-003 확장 자리를 남겨둔 파일입니다.
- 현재 MVP 런타임에는 FALL / INACTIVE만 연결되어 있습니다.
- `list_events`는 로컬 JSONL 저장본을 읽는 개발용 엔드포인트입니다.
