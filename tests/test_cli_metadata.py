import json

from playwright_trace_analyzer.cli import metadata


def test_metadata_json(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(metadata, [str(synthetic_trace_zip), "--format", "json"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert data["browser_name"] == "chromium"
    assert data["platform"] == "Linux"
    assert data["channel"] == "chrome"
    assert data["viewport"]["width"] == 1280
    assert data["viewport"]["height"] == 720
    assert data["base_url"] == "https://example.com"
    assert data["title"] == "my test title"
    assert data["sdk_language"] == "python"
    assert data["playwright_version"] == "130.0.0"
    assert data["duration_ms"] > 0


def test_metadata_markdown(cli_runner, synthetic_trace_zip):
    result = cli_runner.invoke(metadata, [str(synthetic_trace_zip), "--format", "markdown"])

    assert result.exit_code == 0
    assert "chromium" in result.output
    assert "Linux" in result.output
    assert "1280x720" in result.output or ("1280" in result.output and "720" in result.output)
    assert "chrome" in result.output
    assert "my test title" in result.output
