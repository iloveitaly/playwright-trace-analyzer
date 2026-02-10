from playwright_trace_analyzer.models import ScreencastFrame


def extract_screenshots(events: list[dict]) -> list[ScreencastFrame]:
    frames = []

    for event in events:
        if event.get("type") == "screencast-frame":
            frames.append(
                ScreencastFrame(
                    timestamp=event.get("timestamp", 0),
                    page_id=event.get("pageId", ""),
                    sha1=event.get("sha1", ""),
                    width=event.get("width", 0),
                    height=event.get("height", 0),
                )
            )

    frames.sort(key=lambda f: f.timestamp)
    return frames
