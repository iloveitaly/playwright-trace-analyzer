import re
import zipfile
from pathlib import Path

import click

from playwright_trace_analyzer.parser import parse_trace_file
from playwright_trace_analyzer.formatters import json_fmt, markdown


@click.group(invoke_without_command=True)
@click.version_option(package_name="playwright-trace-analyzer")
@click.pass_context
def cli(ctx):
    """Analyze Playwright trace files without the browser-based viewer."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option("--page", "-p", help="Filter by pageId")
@click.option(
    "--last",
    "-n",
    type=int,
    default=20,
    show_default=True,
    help="Number of actions in summary (0 for all)",
)
def summary(trace_file: Path, format: str, page: str | None, last: int):
    """Get a high-level summary of the trace including metadata, errors, console warnings, failed network requests, and action timeline."""
    data = parse_trace_file(trace_file)

    if page:
        data.actions = [a for a in data.actions if a.page_id == page]
        data.console_messages = [m for m in data.console_messages if m.page_id == page]
        data.errors = [e for e in data.errors if e.page_id == page]

    if format == "json":
        output = json_fmt.format_trace_data(data, last)
    else:
        output = markdown.format_trace_data(data, last)

    click.echo(output)


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option("--page", "-p", help="Filter by pageId")
@click.option("--errors-only", is_flag=True, help="Only show failed actions")
def actions(trace_file: Path, format: str, page: str | None, errors_only: bool):
    """View all actions executed during the test with timing, parameters, log messages, and error details."""
    data = parse_trace_file(trace_file)

    filtered_actions = data.actions

    if page:
        filtered_actions = [a for a in filtered_actions if a.page_id == page]

    if errors_only:
        filtered_actions = [a for a in filtered_actions if a.error]

    if format == "json":
        output = json_fmt.format_actions(filtered_actions)
    else:
        output = markdown.format_actions(filtered_actions)

    click.echo(output)


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option("--page", "-p", help="Filter by pageId")
@click.option("--level", help="Filter by message type (error, warning, log, etc.)")
def console(trace_file: Path, format: str, page: str | None, level: str | None):
    """Extract console messages (errors, warnings, logs) with source locations."""
    data = parse_trace_file(trace_file)

    messages = data.console_messages

    if page:
        messages = [m for m in messages if m.page_id == page]

    if level:
        messages = [m for m in messages if m.message_type == level]

    if format == "json":
        output = json_fmt.format_console(messages)
    else:
        output = markdown.format_console(messages)

    click.echo(output)


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option("--failed-only", is_flag=True, help="Only show failed requests")
@click.option("--ignore-pattern", help="Exclude URLs matching regex pattern")
def network(
    trace_file: Path, format: str, failed_only: bool, ignore_pattern: str | None
):
    """Inspect network requests with status codes, timing, content types, and failure details."""
    data = parse_trace_file(trace_file)

    requests = data.network_requests

    if failed_only:
        requests = [r for r in requests if r.status >= 400 or r.failure_text]

    if ignore_pattern:
        pattern = re.compile(ignore_pattern)
        requests = [r for r in requests if not pattern.search(r.url)]

    if format == "json":
        output = json_fmt.format_network(requests)
    else:
        output = markdown.format_network(requests)

    click.echo(output)


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("./trace-screenshots/"),
    show_default=True,
    help="Output directory for screenshots",
)
@click.option("--page", "-p", help="Filter by pageId")
@click.option(
    "--action-only", is_flag=True, help="Only extract action-related screenshots"
)
@click.option(
    "--limit",
    "-n",
    type=int,
    default=0,
    show_default=True,
    help="Maximum number of screenshots to extract (0 for all)",
)
def screenshots(
    trace_file: Path, output_dir: Path, page: str | None, action_only: bool, limit: int
):
    """Extract screenshots embedded in the trace to a directory."""
    from playwright_trace_analyzer.extractors.screenshots import (
        filter_action_frames,
        build_screenshot_filename,
    )

    data = parse_trace_file(trace_file)
    frames = data.screenshots

    if page:
        frames = [f for f in frames if f.page_id == page]

    if action_only:
        frames = filter_action_frames(frames, data.actions)

    if limit > 0:
        frames = frames[-limit:]

    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(trace_file) as zf:
        resource_names = set(zf.namelist())
        screenshot_count = 0

        for frame in frames:
            resource_path = f"resources/{frame.sha1}"

            if resource_path in resource_names:
                output_filename = build_screenshot_filename(
                    frame, data.metadata.trace_start_time
                )
                output_path = output_dir / output_filename

                with zf.open(resource_path) as src:
                    output_path.write_bytes(src.read())
                screenshot_count += 1

    click.echo(f"Extracted {screenshot_count} screenshots to {output_dir}")


@click.command()
@click.argument("trace_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    show_default=True,
    help="Output format",
)
def metadata(trace_file: Path, format: str):
    """View trace metadata including browser, platform, viewport, SDK language, and test duration."""
    data = parse_trace_file(trace_file)

    if format == "json":
        output = json_fmt.format_metadata(data.metadata)
    else:
        output = markdown.format_metadata(data.metadata)

    click.echo(output)


cli.add_command(summary)
cli.add_command(actions)
cli.add_command(console)
cli.add_command(network)
cli.add_command(screenshots)
cli.add_command(metadata)


def main():
    cli()
