import json
import zipfile

import pytest
from click.testing import CliRunner


@pytest.fixture(scope="session")
def synthetic_trace_zip(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("traces")
    trace_path = tmp_dir / "trace.zip"

    trace_events = [
        {
            "type": "context-options",
            "title": "my test title",
            "platform": "Linux",
            "wallTime": 1000.0,
            "monotonicTime": 1000.0,
            "sdkLanguage": "python",
            "contextOptions": {
                "baseURL": "https://example.com",
                "viewport": {"width": 1280, "height": 720},
            },
            "browser": {
                "name": "chromium",
                "version": "130.0.0",
                "channel": "chrome",
            },
            "version": "130.0.0",
        },
        {
            "type": "before",
            "callId": "call-1",
            "startTime": 2500.0,
            "class": "Page",
            "method": "goto",
            "params": {"url": "https://example.com"},
            "pageId": "page@1",
        },
        {
            "type": "log",
            "callId": "call-1",
            "message": "navigating to https://example.com",
            "time": 2700.0,
        },
        {
            "type": "after",
            "callId": "call-1",
            "endTime": 3500.0,
        },
        {
            "type": "before",
            "callId": "call-2",
            "startTime": 4500.0,
            "class": "Locator",
            "method": "click",
            "params": {"selector": "#missing-button"},
            "pageId": "page@2",
        },
        {
            "type": "after",
            "callId": "call-2",
            "endTime": 5500.0,
            "error": {
                "message": "Element not found",
                "stack": "Error: Element not found\n  at Page.click (foo.py:10)",
            },
        },
        {
            "type": "console",
            "messageType": "error",
            "text": "Uncaught TypeError",
            "time": 2800.0,
            "pageId": "page@1",
            "location": {
                "url": "https://example.com/script.js",
                "lineNumber": 42,
                "columnNumber": 10,
            },
        },
        {
            "type": "console",
            "messageType": "warning",
            "text": "deprecated API usage",
            "time": 2900.0,
            "pageId": "page@1",
            "location": {
                "url": "https://example.com/app.js",
                "lineNumber": 100,
            },
        },
        {
            "type": "console",
            "messageType": "log",
            "text": "normal log message",
            "time": 4800.0,
            "pageId": "page@2",
            "location": {
                "url": "https://example.com/page2.js",
                "lineNumber": 5,
                "columnNumber": 15,
            },
        },
        {
            "type": "event",
            "method": "pageError",
            "time": 3000.0,
            "pageId": "page@1",
            "params": {
                "error": {
                    "message": "Runtime error",
                    "stack": "Error: Runtime error\n  at execute (main.js:20)",
                }
            },
        },
        {
            "type": "event",
            "method": "pageerror",
            "time": 5000.0,
            "pageId": "page@2",
            "params": {
                "error": {
                    "message": "Page error on page 2",
                    "stack": "Error: Page error on page 2\n  at handler (page2.js:15)",
                }
            },
        },
        {
            "type": "screencast-frame",
            "pageId": "page@1",
            "sha1": "abc123def456",
            "timestamp": 3000.0,
            "width": 1280,
            "height": 720,
        },
        {
            "type": "screencast-frame",
            "pageId": "page@2",
            "sha1": "xyz789uvw012",
            "timestamp": 5000.0,
            "width": 1280,
            "height": 720,
        },
        {
            "type": "screencast-frame",
            "pageId": "page@1",
            "sha1": "orphan123frame",
            "timestamp": 6000.0,
            "width": 1280,
            "height": 720,
        },
    ]

    network_events = [
        {
            "type": "resource-snapshot",
            "snapshot": {
                "request": {
                    "method": "GET",
                    "url": "https://example.com/api/data",
                },
                "response": {
                    "status": 200,
                    "statusText": "OK",
                    "headers": [{"name": "Content-Type", "value": "application/json"}],
                },
                "timestamp": 2600.0,
                "sizes": {
                    "responseBody": 1024,
                },
            },
        },
        {
            "type": "resource-snapshot",
            "snapshot": {
                "request": {
                    "method": "GET",
                    "url": "https://example.com/missing",
                },
                "response": {
                    "status": 404,
                    "statusText": "Not Found",
                    "headers": [],
                },
                "timestamp": 3200.0,
                "sizes": {
                    "responseBody": 128,
                },
            },
        },
        {
            "type": "resource-snapshot",
            "snapshot": {
                "request": {
                    "method": "POST",
                    "url": "https://example.com/api/submit",
                },
                "response": {
                    "status": 0,
                    "statusText": "",
                    "headers": [],
                },
                "_failureText": "net::ERR_CONNECTION_REFUSED",
                "timestamp": 4700.0,
                "sizes": {
                    "responseBody": 0,
                },
            },
        },
        {
            "type": "request-started",
            "timestamp": 2000.0,
        },
    ]

    with zipfile.ZipFile(trace_path, "w") as zf:
        trace_content = "\n".join(json.dumps(event) for event in trace_events)
        zf.writestr("trace.trace", trace_content)

        network_content = "\n".join(json.dumps(event) for event in network_events)
        zf.writestr("trace.network", network_content)

        zf.writestr("resources/abc123def456", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        zf.writestr("resources/xyz789uvw012", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        zf.writestr("resources/orphan123frame", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    return trace_path


@pytest.fixture
def cli_runner():
    return CliRunner()
