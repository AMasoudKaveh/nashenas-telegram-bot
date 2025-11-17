"""
Simple logger setup for the Nashenas bot.

This module configures a basic application-wide logger that can be imported as:

    from services.logger import logger
"""

import logging


def setup_logger() -> logging.Logger:
    """
    Configure and return the main application logger.

    The logger is configured with:
      - level: INFO
      - format: "<timestamp> - <level> - <message>"
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("nashenas_bot")


logger: logging.Logger = setup_logger()
