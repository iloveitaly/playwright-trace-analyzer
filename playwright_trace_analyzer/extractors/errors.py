from playwright_trace_analyzer.models import TraceError, Action


def extract_errors(events: list[dict], actions: list[Action]) -> list[TraceError]:
    errors = []

    for event in events:
        event_type = event.get("type")

        if event_type == "error":
            errors.append(
                TraceError(
                    time=event.get("timestamp", 0),
                    error_type="error",
                    message=event.get("error", {}).get("message", ""),
                    stack=event.get("error", {}).get("stack"),
                    page_id=event.get("pageId"),
                )
            )
        elif event_type == "page-error":
            page_error = event.get("error", {})
            errors.append(
                TraceError(
                    time=event.get("timestamp", 0),
                    error_type="page-error",
                    message=page_error.get("message", ""),
                    stack=page_error.get("stack"),
                    page_id=event.get("pageId"),
                )
            )

    for action in actions:
        if action.error:
            errors.append(
                TraceError(
                    time=action.start_time,
                    error_type="action-error",
                    message=action.error.error,
                    stack=action.error.stack,
                    page_id=action.page_id,
                )
            )

    errors.sort(key=lambda e: e.time)
    return errors
