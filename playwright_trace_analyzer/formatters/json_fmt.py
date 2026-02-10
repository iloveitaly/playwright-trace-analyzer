import json

from playwright_trace_analyzer.models import (
    TraceData,
    ConsoleMessage,
    NetworkRequest,
    Action,
    TraceMetadata,
)


def format_trace_data(data: TraceData, last_n_actions: int = 20) -> str:
    output = {
        "metadata": data.metadata.model_dump(),
        "errors": [e.model_dump() for e in data.errors],
        "console_errors_warnings": [
            m.model_dump()
            for m in data.console_messages
            if m.message_type in ["error", "warning"]
        ],
        "failed_network_requests": [
            r.model_dump()
            for r in data.network_requests
            if r.status >= 400 or r.failure_text
        ],
        "action_timeline": [
            a.model_dump() for a in _get_last_n_actions(data.actions, last_n_actions)
        ],
    }

    return json.dumps(output, indent=2)


def format_actions(actions: list[Action]) -> str:
    return json.dumps([a.model_dump() for a in actions], indent=2)


def format_console(messages: list[ConsoleMessage]) -> str:
    return json.dumps([m.model_dump() for m in messages], indent=2)


def format_network(requests: list[NetworkRequest]) -> str:
    return json.dumps([r.model_dump() for r in requests], indent=2)


def format_metadata(metadata: TraceMetadata) -> str:
    return json.dumps(metadata.model_dump(), indent=2)


def _get_last_n_actions(actions: list[Action], n: int) -> list[Action]:
    if n == 0:
        return actions
    return actions[-n:] if len(actions) > n else actions
