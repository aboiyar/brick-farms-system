import logging, structlog, sys

def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[structlog.processors.JSONRenderer()]
    )
