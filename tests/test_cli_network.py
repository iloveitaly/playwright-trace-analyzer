import json

from playwright_trace_analyzer.cli import network


def test_network_json(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(network, [str(synthetic_trace_zip), "--format", "json"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 3

    first_request = data[0]
    assert first_request["status"] == 200
    assert first_request["content_type"] == "application/json"

    third_request = data[2]
    assert third_request["failure_text"] is not None


def test_network_markdown(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        network, [str(synthetic_trace_zip), "--format", "markdown"]
    )

    assert result.exit_code == 0
    assert "GET" in result.output or "POST" in result.output
    assert "example.com" in result.output
    assert "200" in result.output or "404" in result.output


def test_network_failed_only(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        network, [str(synthetic_trace_zip), "--format", "json", "--failed-only"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 2

    for req in data:
        assert req["status"] >= 400 or req["failure_text"] is not None


def test_network_ignore_pattern(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(
        network,
        [str(synthetic_trace_zip), "--format", "json", "--ignore-pattern", "missing"],
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert len(data) == 2

    for req in data:
        assert "missing" not in req["url"]
