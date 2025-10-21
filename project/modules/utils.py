"""Utility helpers and configuration for pipeline."""
import os
import logging
import uuid
import time
from functools import wraps


def ensure_dirs(paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def generate_id():
    return uuid.uuid4().hex[:12]


def setup_logger(name=__name__, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        ch = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    logger.setLevel(level)
    return logger


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} took {end-start:.2f}s")
        return res
    return wrapper
