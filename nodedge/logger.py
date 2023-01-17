# -*- coding: utf-8 -*-
"""
Logger module containing function to set up logging functionalities.
"""


import logging
import logging.config
import os

import coloredlogs
import yaml

logger = logging.getLogger(__name__)


def setupLogging(
    defaultPath: str = "logging.yaml",
    defaultLevel: int = logging.DEBUG,
    envKey: str = "LOG_CFG",
):
    """
    Logging Setup
    """
    path = defaultPath
    value = os.getenv(envKey, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install(
                    logger=logging.getLogger(),
                    # level=logging.getLogger().level,
                    fmt=logging.getLogger().handlers[0].formatter._fmt,  # type: ignore
                    reconfigure=True,
                )
                # noinspection PyProtectedMember
            except Exception as e:
                logger.warning(e)
                logger.info("Error in Logging Configuration. Using default configs")
                logging.basicConfig(level=defaultLevel)
                coloredlogs.install(level=defaultLevel)
    else:
        logging.basicConfig(level=defaultLevel)
        coloredlogs.install(level=defaultLevel)
        logger.info("Failed to load configuration file. Using default configs")

    highLightLoggingSetup()


def highLightLoggingSetup():
    logger.debug("Logger configured.")
