# -*- coding: utf-8 -*-
"""
config.py module containing :class:`~nodedge.config.py.<ClassName>` class.
"""
import logging
import sys
from datetime import datetime
from typing import Any

from nodedge.utils import get_project_root, load_config_file

_general_config: dict[str, Any] = load_config_file(
    get_project_root() / "config" / "cfg.yaml"
)

DEBUG: bool = False
if sys.gettrace():
    DEBUG: bool = True

##########
# Logger #
##########
LOGGER_FORMAT: str = _general_config["LOGGER_FORMAT"]
LOGGER_DATE_FORMAT: str = _general_config["LOGGER_DATE_FORMAT"]
LOGGER_LEVEL: str = _general_config["LOGGER_LEVEL"]

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(eval(f"logging.{LOGGER_LEVEL}"))
# logger.setLevel(logging.DEBUG)
_log_formatter = logging.Formatter(fmt=LOGGER_FORMAT, datefmt=LOGGER_DATE_FORMAT)

if DEBUG:
    _logger_filename: str = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}-debugger.log'
else:
    _logger_filename: str = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
