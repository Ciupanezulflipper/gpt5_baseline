# logutil.py
import logging
import os

def setup_logger():
    log_file = os.environ.get("LOG_FILE", "errors.log")
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("forexbot")
