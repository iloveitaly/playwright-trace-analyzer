import io
import zipfile

from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch

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


def _load_image(zf: zipfile.ZipFile, sha1: str) -> Image.Image:
    resource_path = f"resources/{sha1}"
    with zf.open(resource_path) as f:
        img = Image.open(io.BytesIO(f.read()))
        return img.convert("RGBA")


def _images_are_similar(
    img_a: Image.Image, img_b: Image.Image, threshold: float
) -> bool:
    if img_a.size != img_b.size:
        return False

    width, height = img_a.size
    total_pixels = width * height
    diff_count = pixelmatch(img_a, img_b)
    diff_fraction = diff_count / total_pixels

    return diff_fraction <= threshold


def deduplicate_frames(
    frames: list[ScreencastFrame], zf: zipfile.ZipFile, threshold: float = 0.01
) -> list[ScreencastFrame]:
    if not frames:
        return frames

    resource_names = set(zf.namelist())
    result = []
    last_kept_image = None

    for frame in frames:
        resource_path = f"resources/{frame.sha1}"
        if resource_path not in resource_names:
            continue

        try:
            current_image = _load_image(zf, frame.sha1)
        except Exception:
            result.append(frame)
            continue

        if last_kept_image is None:
            result.append(frame)
            last_kept_image = current_image
        elif not _images_are_similar(last_kept_image, current_image, threshold):
            result.append(frame)
            last_kept_image = current_image

    return result
