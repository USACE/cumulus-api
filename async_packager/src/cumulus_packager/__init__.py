"""Initialize package
"""


from ctypes import CDLL, LibraryLoader
import logging
import sys

from cumulus_packager.configurations import LOGGER_LEVEL


# ------------------------- #
# Custom handler that flushes immediately after each log
# This ensures logs are not lost if process is killed (OOM, segfault, etc.)
# ------------------------- #
class FlushingStreamHandler(logging.StreamHandler):
    """StreamHandler that flushes after every emit to prevent log loss on crash."""

    def emit(self, record):
        super().emit(record)
        self.flush()


# ------------------------- #
# setup the logging for the package
# ------------------------- #
class package_logger(logging.Logger):
    """Package logger extending logging.Logger

    Parameters
    ----------
    logging : Logger
        Logger object
    """

    def __init__(self):
        super().__init__(__package__)

        self.log_level = "info"

        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] "
            + "{%(name)s:%(funcName)s} - %(levelname)-s - %(message)s",
            "%Y-%m-%dT%H:%M:%S",
        )

        # Use FlushingStreamHandler to ensure logs are written immediately
        # This prevents log loss when process is killed (OOM, segfault, SIGKILL)
        ch = FlushingStreamHandler(sys.stderr)

        ch.setFormatter(formatter)
        self.addHandler(ch)

    @property
    def log_level(self):
        return logging._levelToName[self.level]

    @log_level.setter
    def log_level(self, level):
        level = logging._nameToLevel[level.upper()] if isinstance(level, str) else level
        self.setLevel(level)


# create a logger for the package and set the logging level from env vars
logger = package_logger()
logger.log_level = LOGGER_LEVEL
