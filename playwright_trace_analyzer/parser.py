import json
import zipfile
from collections import defaultdict
from pathlib import Path

from playwright_trace_analyzer.models import TraceData


def parse_trace_file(trace_path: Path) -> TraceData:
    with zipfile.ZipFile(trace_path) as zf:
        events = _extract_events(zf)

        from playwright_trace_analyzer.extractors.metadata import extract_metadata
        from playwright_trace_analyzer.extractors.actions import extract_actions
        from playwright_trace_analyzer.extractors.console import (
            extract_console_messages,
        )
        from playwright_trace_analyzer.extractors.network import (
            extract_network_requests,
        )
        from playwright_trace_analyzer.extractors.errors import extract_errors
        from playwright_trace_analyzer.extractors.screenshots import extract_screenshots

        metadata = extract_metadata(events)
        actions = extract_actions(events)
        console_messages = extract_console_messages(events)
        network_requests = extract_network_requests(zf, events)
        errors = extract_errors(events, actions)
        screenshots = extract_screenshots(events)

        return TraceData(
            metadata=metadata,
            actions=actions,
            console_messages=console_messages,
            network_requests=network_requests,
            errors=errors,
            screenshots=screenshots,
        )


def _extract_events(zf: zipfile.ZipFile) -> list[dict]:
    events = []

    for name in zf.namelist():
        if name.endswith(".trace"):
            with zf.open(name) as f:
                for line in f:
                    line = line.decode("utf-8").strip()
                    if line:
                        events.append(json.loads(line))

    events.sort(key=lambda e: e.get("timestamp", 0))
    return events


def group_events_by_type(events: list[dict]) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for event in events:
        event_type = event.get("type")
        if event_type:
            groups[event_type].append(event)
    return dict(groups)


def group_events_by_call_id(events: list[dict]) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for event in events:
        call_id = event.get("callId")
        if call_id:
            groups[call_id].append(event)
    return dict(groups)
