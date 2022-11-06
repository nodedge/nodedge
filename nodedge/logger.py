# -*- coding: utf-8 -*-
"""
Logger module containing function to set up logging functionalities.
"""


import logging
import logging.config
import os

import coloredlogs
import yaml

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


def setupLogging(
    defaultPath: str = "../logging.yaml",
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
                # noinspection PyProtectedMember
                coloredlogs.install(
                    level=logging.getLogger().level,
                    fmt=logging.getLogger().handlers[0].formatter._fmt,  # type: ignore
                )
            except Exception as e:
                print(e)
                print("Error in Logging Configuration. Using default configs")
                logging.basicConfig(level=defaultLevel)
                coloredlogs.install(level=defaultLevel)
    else:
        logging.basicConfig(level=defaultLevel)
        coloredlogs.install(level=defaultLevel)
        print("Failed to load configuration file. Using default configs")


def highLightLoggingSetup():
    logging.debug("DEBUG is being sent")
    logging.info("INFO is being sent")
    logging.warning("WARNING is being sent")
    logging.error("ERROR is being sent")
    logging.critical("CRITICAL is being sent")
