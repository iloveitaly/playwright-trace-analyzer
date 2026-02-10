[![Release Notes](https://img.shields.io/github/release/iloveitaly/playwright-trace-analyzer)](https://github.com/iloveitaly/playwright-trace-analyzer/releases)
[![Downloads](https://static.pepy.tech/badge/playwright-trace-analyzer/month)](https://pepy.tech/project/playwright-trace-analyzer)
![GitHub CI Status](https://github.com/iloveitaly/playwright-trace-analyzer/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Playwright Trace File Analyzer

A command-line tool for analyzing Playwright trace files without opening the browser-based trace viewer. When you have failing Playwright tests and need to debug them programmatically or in CI/CD environments, this tool extracts structured data from trace.zip files.

I built this because I wanted to parse Playwright traces in automated workflows - extracting errors, console messages, and network failures without spinning up the Playwright trace viewer UI. It's particularly useful for debugging tests in CI where you can't easily open the trace viewer, or when you need to process trace data programmatically.

## Installation

```bash
uv add playwright-trace-analyzer
```

## Usage

The tool provides several subcommands for analyzing different aspects of your Playwright traces:

```bash
# Get a high-level summary of the trace
playwright-trace-analyzer summary trace.zip

# View all actions executed during the test
playwright-trace-analyzer actions trace.zip --errors-only

# Extract console messages and warnings
playwright-trace-analyzer console trace.zip --level error

# Check failed network requests
playwright-trace-analyzer network trace.zip --failed-only

# Extract screenshots from the trace
playwright-trace-analyzer screenshots trace.zip -o ./screenshots

# View trace metadata
playwright-trace-analyzer metadata trace.zip
```

All commands support JSON and markdown output formats:

```bash
playwright-trace-analyzer summary trace.zip --format markdown
playwright-trace-analyzer actions trace.zip --format json
```

Filter by page ID when dealing with multi-page traces:

```bash
playwright-trace-analyzer summary trace.zip --page "page@1"
```

## Features

* Extract structured data from Playwright trace.zip files
* View test actions with timing, parameters, and error details
* Analyze console messages (errors, warnings, logs) with source locations
* Inspect network requests including failures and status codes
* Extract screenshots embedded in traces
* Filter data by page ID, error status, or custom patterns
* Output in JSON or markdown formats for further processing
* No need for browser or Playwright trace viewer UI

## [MIT License](LICENSE.md)

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
