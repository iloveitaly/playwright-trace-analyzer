from playwright_trace_analyzer.models import ScreencastFrame, Action


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


def filter_action_frames(
    frames: list[ScreencastFrame], actions: list[Action]
) -> list[ScreencastFrame]:
    filtered = []

    for frame in frames:
        for action in actions:
            if action.page_id != frame.page_id:
                continue

            if action.end_time is None:
                continue

            if action.start_time <= frame.timestamp <= action.end_time:
                filtered.append(frame)
                break

    return filtered


def build_screenshot_filename(frame: ScreencastFrame, trace_start_time: float) -> str:
    relative_ms = int(frame.timestamp - trace_start_time)
    return f"{relative_ms}ms.jpeg"
