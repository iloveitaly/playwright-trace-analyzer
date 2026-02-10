import json
import zipfile

from playwright_trace_analyzer.models import NetworkRequest


def extract_network_requests(zf: zipfile.ZipFile, _events: list[dict]) -> list[NetworkRequest]:
    requests = []

    for name in zf.namelist():
        if name.endswith(".network"):
            with zf.open(name) as f:
                for line in f:
                    line = line.decode("utf-8").strip()
                    if not line:
                        continue

                    entry = json.loads(line)

                    if entry.get("type") != "resource-snapshot":
                        continue

                    snapshot = entry.get("snapshot", {})
                    request = snapshot.get("request", {})
                    response = snapshot.get("response", {})
                    timings = snapshot.get("timings", {})

                    status = response.get("status", 0)
                    duration = sum(
                        timings.get(k, 0)
                        for k in ["dns", "connect", "ssl", "send", "wait", "receive"]
                    )

                    response_size = 0
                    content = response.get("content", {})
                    if content:
                        response_size = content.get("size", 0)

                    content_type = None
                    for header in response.get("headers", []):
                        if header.get("name", "").lower() == "content-type":
                            content_type = header.get("value")
                            break

                    requests.append(
                        NetworkRequest(
                            method=request.get("method", "GET"),
                            url=request.get("url", ""),
                            status=status,
                            status_text=response.get("statusText", ""),
                            failure_text=snapshot.get("_failureText"),
                            was_aborted=snapshot.get("_wasAborted", False),
                            duration_ms=duration,
                            response_size=response_size,
                            content_type=content_type,
                        )
                    )

    return requests
