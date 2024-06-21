import logging
import sys
import time
from typing import Optional

logger = logging.getLogger(__name__)


def countdown(seconds: int, msg: Optional[str] = None) -> None:
    logger_msg = msg if msg is not None else f"Waiting for {seconds} seconds"
    logger.info(logger_msg)
    for remaining in range(seconds, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(f"{remaining:2d} seconds remaining.")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\nCompleted!")
