"""Test playwright-trace-analyzer."""

import playwright_trace_analyzer


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(playwright_trace_analyzer.__name__, str)
