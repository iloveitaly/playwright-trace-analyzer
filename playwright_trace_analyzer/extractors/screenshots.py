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
    best_per_action: dict[str, ScreencastFrame] = {}

    for action in actions:
        if action.end_time is None:
            continue

        for frame in frames:
            if action.page_id != frame.page_id:
                continue

            if not (action.start_time <= frame.timestamp <= action.end_time):
                continue

            existing = best_per_action.get(action.call_id)
            if existing is None or frame.timestamp > existing.timestamp:
                best_per_action[action.call_id] = frame

    result = list(best_per_action.values())
    result.sort(key=lambda f: f.timestamp)
    return result


def build_screenshot_filename(frame: ScreencastFrame, trace_start_time: float) -> str:
    relative_ms = int(frame.timestamp - trace_start_time)
    return f"{relative_ms}ms.jpeg"
