from playwright_trace_analyzer.models import Action, ActionError, LogMessage
from playwright_trace_analyzer.parser import group_events_by_call_id


def extract_actions(events: list[dict]) -> list[Action]:
    call_groups = group_events_by_call_id(events)
    actions = []

    for call_id, call_events in call_groups.items():
        before_event = next((e for e in call_events if e.get("type") == "before"), None)
        if not before_event:
            continue

        after_event = next((e for e in call_events if e.get("type") == "after"), None)
        log_events = [e for e in call_events if e.get("type") == "log"]

        params = before_event.get("params", {})
        start_time = before_event.get("startTime", 0)
        end_time = after_event.get("endTime") if after_event else None

        error = None
        if after_event and after_event.get("error"):
            error_data = after_event["error"]
            error = ActionError(
                error=error_data.get("message", ""),
                stack=error_data.get("stack"),
            )

        log_messages = [
            LogMessage(
                time=log_event.get("time", 0),
                message=log_event.get("message", ""),
            )
            for log_event in log_events
        ]

        actions.append(
            Action(
                call_id=call_id,
                title=before_event.get("title"),
                class_name=before_event.get("class", ""),
                method=before_event.get("method", ""),
                params=params,
                start_time=start_time,
                end_time=end_time,
                page_id=before_event.get("pageId"),
                error=error,
                log_messages=log_messages,
            )
        )

    actions.sort(key=lambda a: a.start_time)
    return actions
