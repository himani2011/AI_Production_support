import logging
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIRECTORY / "application.log"

LOG_DIRECTORY.mkdir(exist_ok=True)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("ecommerce")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()