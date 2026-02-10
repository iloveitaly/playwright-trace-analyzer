from structlog_config import configure_logger

from playwright_trace_analyzer.cli import main

__all__ = ["main"]

logger = configure_logger()
