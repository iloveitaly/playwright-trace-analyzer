import json

from playwright_trace_analyzer.cli import summary


def test_summary_json(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(summary, [str(synthetic_trace_zip), "--format", "json"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert "metadata" in data
    assert "errors" in data
    assert "console_errors_warnings" in data
    assert "failed_network_requests" in data
    assert "action_timeline" in data


def test_summary_markdown(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(summary, [str(synthetic_trace_zip), "--format", "markdown"])

    assert result.exit_code == 0
    assert "# Metadata" in result.output
    assert "# Errors" in result.output
    assert "# Action Timeline" in result.output


def test_summary_page_filter(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(summary, [str(synthetic_trace_zip), "--format", "json", "--page", "page@1"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    for action in data["action_timeline"]:
        assert action["page_id"] == "page@1"

    for console_msg in data["console_errors_warnings"]:
        assert console_msg["page_id"] == "page@1"


def test_summary_last_n(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(summary, [str(synthetic_trace_zip), "--format", "json", "--last", "1"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data["action_timeline"]) == 1


def test_summary_last_zero(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(summary, [str(synthetic_trace_zip), "--format", "json", "--last", "0"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data["action_timeline"]) == 2
