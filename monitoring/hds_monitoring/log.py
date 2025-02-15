import logging
import logging.handlers
import os

from hds_monitoring import config

ROTATING_FILE_HANDLER = logging.handlers.RotatingFileHandler(
    filename=os.path.join(config.config["log_dir"], "hds-monitoring.log"),
    maxBytes=20000000,
    backupCount=5,
)

LEVEL_MAPPING = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=LEVEL_MAPPING.get(config.config["log_level"].lower(), logging.INFO),
    handlers=[ROTATING_FILE_HANDLER],
)


def get_logger(name):
    return logging.getLogger(name)
