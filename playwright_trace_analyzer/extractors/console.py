from playwright_trace_analyzer.models import ConsoleMessage, SourceLocation


def extract_console_messages(events: list[dict]) -> list[ConsoleMessage]:
    messages = []

    for event in events:
        if event.get("type") == "console":
            location_data = event.get("location", {})
            location = SourceLocation(
                url=location_data.get("url", ""),
                line_number=location_data.get("lineNumber"),
                column_number=location_data.get("columnNumber"),
            )

            messages.append(
                ConsoleMessage(
                    time=event.get("timestamp", 0),
                    page_id=event.get("pageId"),
                    message_type=event.get("messageType", "log"),
                    text=event.get("text", ""),
                    location=location,
                )
            )

    messages.sort(key=lambda m: m.time)
    return messages
