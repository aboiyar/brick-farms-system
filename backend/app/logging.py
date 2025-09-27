import logging, structlog, sys


def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[structlog.processors.JSONRenderer()]
    )


def exception_logger(exc: Exception, request_id: str | None = None, extra: dict | None = None):
    """Log an exception with optional external request id and extra context.

    Args:
        exc: The exception instance.
        request_id: Optional external request id (from API gateway or service).
        extra: Optional dictionary with extra context to include in logs.
    """
    logger = structlog.get_logger()
    payload = {"error": str(exc)}
    if request_id:
        payload["external_request_id"] = request_id
    if extra:
        payload.update(extra)
    # log exception info -> stack trace in message
    logger.error("exception_occurred", **payload, exc_info=True)
