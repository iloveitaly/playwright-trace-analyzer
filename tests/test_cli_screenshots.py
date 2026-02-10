from playwright_trace_analyzer.cli import screenshots


def test_screenshots_default(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots"
    result = cli_runner.invoke(
        screenshots, [str(synthetic_trace_zip), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0
    assert "Extracted 2 screenshots" in result.output

    assert output_dir.exists()
    files = list(output_dir.iterdir())
    assert len(files) == 2


def test_screenshots_action_only(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_action"
    result = cli_runner.invoke(
        screenshots,
        [str(synthetic_trace_zip), "--output-dir", str(output_dir), "--action-only"],
    )

    assert result.exit_code == 0
    assert "Extracted 0 screenshots" in result.output


def test_screenshots_creates_output_dir(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "nested" / "deeply" / "screenshots"
    result = cli_runner.invoke(
        screenshots, [str(synthetic_trace_zip), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0
    assert output_dir.exists()
