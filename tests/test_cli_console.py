import json

from playwright_trace_analyzer.cli import console


def test_console_json(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(console, [str(synthetic_trace_zip), "--format", "json"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 3

    types = [msg["message_type"] for msg in data]
    assert "error" in types
    assert "warning" in types
    assert "log" in types

    for msg in data:
        assert "location" in msg
        assert "url" in msg["location"]


def test_console_markdown(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        console, [str(synthetic_trace_zip), "--format", "markdown"]
    )

    assert result.exit_code == 0
    assert "[ERROR]" in result.output or "error" in result.output.lower()
    assert "[WARNING]" in result.output or "warning" in result.output.lower()
    assert "[LOG]" in result.output or "log" in result.output.lower()


def test_console_page_filter(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        console, [str(synthetic_trace_zip), "--format", "json", "--page", "page@2"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["page_id"] == "page@2"
    assert data[0]["message_type"] == "log"


def test_console_level_filter(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        console, [str(synthetic_trace_zip), "--format", "json", "--level", "error"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["message_type"] == "error"
