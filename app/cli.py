import argparse
from pathlib import Path

from app.service import Analyzer



def main() -> None:
    p = argparse.ArgumentParser(description="Analyze a safety demo video")
    p.add_argument("--resident", type=int, required=True, help="resident id")
    p.add_argument("--video", type=str, required=True, help="video file path")
    p.add_argument("--notify", action="store_true", help="send event to server")
    args = p.parse_args()

    res = Analyzer().run(
        video_path=args.video,
        resident_id=args.resident,
        video_name=Path(args.video).name,
        notify=args.notify,
    )
    print(res.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
