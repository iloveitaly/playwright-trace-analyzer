from playwright_trace_analyzer.models import TraceMetadata, Size


def extract_metadata(events: list[dict]) -> TraceMetadata:
    context_event = next(
        (e for e in events if e.get("type") == "context-options"),
        {}
    )

    options = context_event.get("contextOptions", {})
    browser = context_event.get("browser", {})
    platform_data = context_event.get("platform", {})

    start_time = min((e.get("timestamp", 0) for e in events if e.get("timestamp")), default=0)
    end_time = max((e.get("timestamp", 0) for e in events if e.get("timestamp")), default=0)
    duration_ms = end_time - start_time

    viewport_data = options.get("viewport")
    viewport = Size(**viewport_data) if viewport_data else None

    if isinstance(platform_data, dict):
        platform_name = platform_data.get("name", "unknown")
    else:
        platform_name = str(platform_data) if platform_data else "unknown"

    if isinstance(browser, dict):
        browser_name = browser.get("name", "unknown")
        channel = browser.get("channel")
    else:
        browser_name = str(browser) if browser else "unknown"
        channel = None

    version = context_event.get("version")
    version_str = str(version) if version is not None else None

    return TraceMetadata(
        browser_name=browser_name,
        channel=channel,
        platform=platform_name,
        playwright_version=version_str,
        sdk_language=context_event.get("sdkLanguage"),
        title=context_event.get("title"),
        wall_time=context_event.get("wallTime", 0),
        base_url=options.get("baseURL"),
        viewport=viewport,
        duration_ms=duration_ms,
    )
