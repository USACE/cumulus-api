"""Initialize package
"""


import logging

from cumulus_geoproc.configurations import LOGGER_LEVEL


# ------------------------- #
# setup the logging for the package
# ------------------------- #
class package_logger(logging.Logger):
    def __init__(self):
        super().__init__(__package__)

        self.log_level = "info"

        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] "
            + "{%(name)s:%(funcName)s} - %(levelname)-s - %(message)s",
            "%Y-%m-%dT%H:%M:%S",
        )

        ch = logging.StreamHandler()

        ch.setFormatter(formatter)
        self.addHandler(ch)

    @property
    def log_level(self):
        return logging._levelToName[self.level]

    @log_level.setter
    def log_level(self, level):
        level = logging._nameToLevel[level.upper()] if isinstance(level, str) else level
        self.setLevel(level)


logger = package_logger()
logger.log_level = LOGGER_LEVEL
