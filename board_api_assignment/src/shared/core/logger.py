import os
import logging
from dotenv import load_dotenv

load_dotenv()

log_mode = os.getenv("LOGGING_MODE", "info").lower()
log_level = logging.DEBUG if log_mode == "debug" else logging.INFO

LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=log_level,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    force=True,
)


def get_logger(name: str | None = None) -> logging.Logger:
    logger_name = name or os.getenv("LOGGER_NAME", "app")
    return logging.getLogger(logger_name)


logger = get_logger()
