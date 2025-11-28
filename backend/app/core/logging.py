import logging
import logging.handlers
import os
import sys
import structlog
from typing import Any, Dict

def configure_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """
    Configures structured logging for the application.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard python logging
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler (Rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setFormatter(formatter)

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    root_logger.handlers = [console_handler, file_handler]
    
    # Intercept standard library logs
    logging.getLogger("uvicorn.access").handlers = [console_handler, file_handler]
    logging.getLogger("uvicorn.error").handlers = [console_handler, file_handler]

    # Silence noisy libraries if needed
    # logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str):
    return structlog.get_logger(name)
