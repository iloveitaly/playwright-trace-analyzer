import re

from playwright_trace_analyzer.cli import screenshots


def test_screenshots_default(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots"
    result = cli_runner.invoke(
        screenshots, [str(synthetic_trace_zip), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0
    assert "Extracted 3 screenshots" in result.output

    assert output_dir.exists()
    files = list(output_dir.iterdir())
    assert len(files) == 3

    for file in files:
        assert re.match(r"\d+ms\.jpeg$", file.name)


def test_screenshots_action_only(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_action"
    result = cli_runner.invoke(
        screenshots,
        [str(synthetic_trace_zip), "--output-dir", str(output_dir), "--action-only"],
    )

    assert result.exit_code == 0
    assert "Extracted 2 screenshots" in result.output

    files = list(output_dir.iterdir())
    assert len(files) == 2


def test_screenshots_action_only_with_limit(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_action_limit"
    result = cli_runner.invoke(
        screenshots,
        [
            str(synthetic_trace_zip),
            "--output-dir",
            str(output_dir),
            "--action-only",
            "--limit",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "Extracted 1 screenshot" in result.output

    files = list(output_dir.iterdir())
    assert len(files) == 1


def test_screenshots_page_filter(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_page"
    result = cli_runner.invoke(
        screenshots,
        [str(synthetic_trace_zip), "--output-dir", str(output_dir), "--page", "page@1"],
    )

    assert result.exit_code == 0
    assert "Extracted 2 screenshots" in result.output

    files = list(output_dir.iterdir())
    assert len(files) == 2


def test_screenshots_limit(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_limit"
    result = cli_runner.invoke(
        screenshots,
        [str(synthetic_trace_zip), "--output-dir", str(output_dir), "--limit", "1"],
    )

    assert result.exit_code == 0
    assert "Extracted 1 screenshot" in result.output

    files = list(output_dir.iterdir())
    assert len(files) == 1


def test_screenshots_creates_output_dir(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "nested" / "deeply" / "screenshots"
    result = cli_runner.invoke(
        screenshots, [str(synthetic_trace_zip), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0
    assert output_dir.exists()


def test_screenshots_filenames(cli_runner, synthetic_trace_zip, tmp_path):
    output_dir = tmp_path / "screenshots_names"
    result = cli_runner.invoke(
        screenshots, [str(synthetic_trace_zip), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0

    files = sorted([f.name for f in output_dir.iterdir()])
    assert files == ["2000ms.jpeg", "4000ms.jpeg", "5000ms.jpeg"]
