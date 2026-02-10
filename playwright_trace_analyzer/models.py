from pydantic import BaseModel


class Size(BaseModel):
    width: int
    height: int


class TraceMetadata(BaseModel):
    browser_name: str
    channel: str | None = None
    platform: str
    playwright_version: str | None = None
    sdk_language: str | None = None
    title: str | None = None
    wall_time: float
    base_url: str | None = None
    viewport: Size | None = None
    duration_ms: float


class SourceLocation(BaseModel):
    url: str
    line_number: int | None = None
    column_number: int | None = None


class LogMessage(BaseModel):
    time: float
    message: str


class ActionError(BaseModel):
    error: str
    stack: str | None = None


class Action(BaseModel):
    call_id: str
    title: str | None = None
    class_name: str
    method: str
    params: dict[str, object]
    start_time: float
    end_time: float | None = None
    page_id: str | None = None
    error: ActionError | None = None
    log_messages: list[LogMessage] = []


class ConsoleMessage(BaseModel):
    time: float
    page_id: str | None = None
    message_type: str
    text: str
    location: SourceLocation


class NetworkRequest(BaseModel):
    method: str
    url: str
    status: int
    status_text: str
    failure_text: str | None = None
    was_aborted: bool = False
    duration_ms: float
    response_size: int
    content_type: str | None = None


class TraceError(BaseModel):
    time: float
    error_type: str
    message: str
    stack: str | None = None
    page_id: str | None = None


class ScreencastFrame(BaseModel):
    timestamp: float
    page_id: str
    sha1: str
    width: int
    height: int


class TraceData(BaseModel):
    metadata: TraceMetadata
    actions: list[Action]
    console_messages: list[ConsoleMessage]
    network_requests: list[NetworkRequest]
    errors: list[TraceError]
    screenshots: list[ScreencastFrame]
