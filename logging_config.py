"""
trading_bot.bot.logging_config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Centralized logging configuration.
All log records — INFO, WARNING, ERROR — are written to trading_bot.log.
"""

import logging
import sys
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[2] / "trading_bot.log"

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger that writes to both the log file and stdout.

    Parameters
    ----------
    name:
        Typically ``__name__`` of the calling module.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured — avoid duplicate handlers

    logger.setLevel(logging.DEBUG)

    # --- file handler (always DEBUG+) ---
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)

    # --- stream handler (INFO+ so the terminal stays clean) ---
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(_FORMATTER)

    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.propagate = False

    return logger