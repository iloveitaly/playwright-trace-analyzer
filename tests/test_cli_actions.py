import json

from playwright_trace_analyzer.cli import actions


def test_actions_json(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(actions, [str(synthetic_trace_zip), "--format", "json"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 2

    first_action = data[0]
    assert first_action["call_id"] == "call-1"
    assert first_action["error"] is None
    assert len(first_action["log_messages"]) > 0

    second_action = data[1]
    assert second_action["call_id"] == "call-2"
    assert second_action["error"] is not None
    assert "Element not found" in second_action["error"]["error"]
    assert second_action["error"]["stack"] is not None


def test_actions_markdown(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        actions, [str(synthetic_trace_zip), "--format", "markdown"]
    )

    assert result.exit_code == 0
    assert "Page" in result.output
    assert "goto" in result.output
    assert "Locator" in result.output
    assert "click" in result.output
    assert "FAILED" in result.output or "Element not found" in result.output


def test_actions_page_filter(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        actions, [str(synthetic_trace_zip), "--format", "json", "--page", "page@2"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["page_id"] == "page@2"


def test_actions_errors_only(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        actions, [str(synthetic_trace_zip), "--format", "json", "--errors-only"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["error"] is not None
