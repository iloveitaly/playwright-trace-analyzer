from playwright_trace_analyzer.cli import cli


def test_help_output(cli_runner):
    result = cli_runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "summary" in result.output
    assert "actions" in result.output
    assert "console" in result.output
    assert "network" in result.output
    assert "screenshots" in result.output
    assert "metadata" in result.output


def test_version(cli_runner):
    result = cli_runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output
