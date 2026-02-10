from playwright_trace_analyzer.models import (
    TraceData,
    ConsoleMessage,
    NetworkRequest,
    Action,
    TraceMetadata,
)


def format_trace_data(data: TraceData, last_n_actions: int = 20) -> str:
    sections = []

    sections.append(_format_metadata_section(data.metadata))

    if data.errors:
        sections.append(_format_errors_section(data.errors))

    console_errors_warnings = [
        m for m in data.console_messages if m.message_type in ["error", "warning"]
    ]
    if console_errors_warnings:
        sections.append(_format_console_errors_section(console_errors_warnings))

    failed_requests = [
        r for r in data.network_requests if r.status >= 400 or r.failure_text
    ]
    if failed_requests:
        sections.append(_format_failed_requests_section(failed_requests))

    sections.append(_format_action_timeline_section(data.actions, last_n_actions))

    return "\n\n".join(sections)


def format_actions(actions: list[Action]) -> str:
    lines = ["# Actions\n"]

    for action in actions:
        status = "❌ FAILED" if action.error else "✓"
        duration = ""
        if action.end_time:
            duration_ms = action.end_time - action.start_time
            duration = f" ({duration_ms:.2f}ms)"

        lines.append(f"## {status} {action.class_name}.{action.method}{duration}")
        lines.append(f"**Call ID:** {action.call_id}")

        if action.title:
            lines.append(f"**Title:** {action.title}")

        if action.params:
            lines.append(f"**Params:** `{action.params}`")

        if action.error:
            lines.append(f"\n**Error:** {action.error.error}")
            if action.error.stack:
                lines.append(f"```\n{action.error.stack}\n```")

        if action.log_messages:
            lines.append("\n**Logs:**")
            for log in action.log_messages:
                lines.append(f"- {log.message}")

        lines.append("")

    return "\n".join(lines)


def format_console(messages: list[ConsoleMessage]) -> str:
    lines = ["# Console Messages\n"]

    for msg in messages:
        lines.append(f"## [{msg.message_type.upper()}] {msg.text}")
        lines.append(f"**Location:** {msg.location.url}")
        if msg.location.line_number:
            lines.append(f"**Line:** {msg.location.line_number}")
        lines.append("")

    return "\n".join(lines)


def format_network(requests: list[NetworkRequest]) -> str:
    lines = ["# Network Requests\n"]

    for req in requests:
        status_icon = "❌" if req.status >= 400 or req.failure_text else "✓"
        lines.append(f"## {status_icon} {req.method} {req.url}")
        lines.append(f"**Status:** {req.status} {req.status_text}")
        lines.append(f"**Duration:** {req.duration_ms:.2f}ms")
        lines.append(f"**Size:** {req.response_size} bytes")

        if req.content_type:
            lines.append(f"**Content-Type:** {req.content_type}")

        if req.failure_text:
            lines.append(f"**Failure:** {req.failure_text}")

        lines.append("")

    return "\n".join(lines)


def format_metadata(metadata: TraceMetadata) -> str:
    return _format_metadata_section(metadata)


def _format_metadata_section(metadata: TraceMetadata) -> str:
    lines = ["# Metadata"]
    lines.append(f"**Browser:** {metadata.browser_name}")
    if metadata.channel:
        lines.append(f"**Channel:** {metadata.channel}")
    lines.append(f"**Platform:** {metadata.platform}")
    if metadata.playwright_version:
        lines.append(f"**Playwright Version:** {metadata.playwright_version}")
    if metadata.title:
        lines.append(f"**Test Title:** {metadata.title}")
    if metadata.base_url:
        lines.append(f"**Base URL:** {metadata.base_url}")
    if metadata.viewport:
        lines.append(
            f"**Viewport:** {metadata.viewport.width}x{metadata.viewport.height}"
        )
    lines.append(f"**Duration:** {metadata.duration_ms:.2f}ms")

    return "\n".join(lines)


def _format_errors_section(errors) -> str:
    lines = ["# Errors"]

    for error in errors:
        lines.append(f"## [{error.error_type}] {error.message}")
        if error.stack:
            lines.append(f"```\n{error.stack}\n```")
        lines.append("")

    return "\n".join(lines)


def _format_console_errors_section(messages: list[ConsoleMessage]) -> str:
    lines = ["# Console Errors & Warnings"]

    for msg in messages:
        lines.append(f"## [{msg.message_type.upper()}] {msg.text}")
        lines.append(f"**Location:** {msg.location.url}")
        lines.append("")

    return "\n".join(lines)


def _format_failed_requests_section(requests: list[NetworkRequest]) -> str:
    lines = ["# Failed Network Requests"]

    for req in requests:
        lines.append(f"## {req.method} {req.url}")
        lines.append(f"**Status:** {req.status} {req.status_text}")
        if req.failure_text:
            lines.append(f"**Failure:** {req.failure_text}")
        lines.append("")

    return "\n".join(lines)


def _format_action_timeline_section(actions: list[Action], last_n: int) -> str:
    display_actions = (
        actions[-last_n:] if last_n > 0 and len(actions) > last_n else actions
    )

    lines = ["# Action Timeline"]
    if last_n > 0 and len(actions) > last_n:
        lines.append(f"*(Showing last {last_n} of {len(actions)} actions)*\n")

    for action in display_actions:
        status = "❌" if action.error else "✓"
        duration = ""
        if action.end_time:
            duration_ms = action.end_time - action.start_time
            duration = f" ({duration_ms:.2f}ms)"

        title = action.title or f"{action.class_name}.{action.method}"
        lines.append(f"- {status} {title}{duration}")

        if action.error:
            lines.append(f"  - **Error:** {action.error.error}")

    return "\n".join(lines)
