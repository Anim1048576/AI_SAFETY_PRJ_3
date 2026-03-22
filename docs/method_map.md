# 메서드 맵

## app/main.py

### `health()`
- 역할: 서버 생존 확인
- 입력: 없음
- 출력: `{ ok, app }`

### `analyze_video()`
- 역할: 업로드된 동영상을 임시 파일로 저장한 뒤 분석 실행
- 입력: `resident_id`, `video`, `notify`
- 처리:
  1. 업로드 파일을 임시 파일로 저장
  2. `Analyzer.run()` 호출
  3. 결과 JSON 반환
  4. 임시 파일 삭제
- 출력: `AnalyzeRes`

## app/service.py

### `run()`
- 역할: 전체 프레임 루프를 돌며 FALL / INACTIVE 이벤트를 평가
- 입력: `video_path`, `resident_id`, `video_name`, `notify`
- 처리:
  1. 비디오 프레임 순회
  2. 포즈 추출
  3. 낙상 판정
  4. 무응답 판정
  5. 이벤트 생성/저장/선택 전송
- 출력: `AnalyzeRes`

### `_make_evt()`
- 역할: 내부 감지 결과를 API 응답용 이벤트 객체로 변환
- 입력: 프레임, resident id, 이벤트 종류, 설명, metrics
- 출력: `Evt`

## app/detectors/fall.py

### `load()`
- 역할: MediaPipe Pose 준비
- 입력: 없음
- 출력: 없음

### `read()`
- 역할: 프레임에서 관절 좌표와 낙상 판정용 특징 추출
- 입력: `frame`
- 출력: `PoseHit`

### `flat()`
- 역할: 현재 프레임이 수평 자세 후보인지 확인
- 입력: `PoseHit`
- 출력: `bool`

### `tick()`
- 역할: 수평 자세 유지 시간을 누적하고 FALL 발생 여부 판단
- 입력: `PoseHit`, `sec`
- 출력: `dict | None`

## app/detectors/inactive.py

### `motion()`
- 역할: 프레임의 움직임 비율 계산
- 입력: `frame`
- 출력: `float`

### `day_score()`
- 역할: 분석 중 누적된 평균 활동량 점수 반환
- 입력: 없음
- 출력: `float`

### `tick()`
- 역할: 사람이 있는 상태에서 무움직임 시간을 누적하고 INACTIVE 발생 여부 판단
- 입력: `frame`, `sec`, `seen`
- 출력: `dict | None`

### `reset()`
- 역할: 무응답 누적 상태 초기화
- 입력: 없음
- 출력: 없음

## app/notifier.py

### `sleep()`
- 역할: 서버/설정 기반 취침 시간대 값을 돌려주는 자리
- 입력: `resident_id`
- 출력: `SleepRes`

### `send()`
- 역할: 이벤트 전송 1회 시도
- 입력: `Evt`
- 출력: 전송 결과 dict

### `retry()`
- 역할: 재시도 포함 POST 전송
- 입력: `dict`
- 출력: 전송 결과 dict
