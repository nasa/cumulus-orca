# copied from shared_db.py
# Retry decorator for functions
import functools
import random
import time
from logging import Logger
from typing import Callable, TypeVar

RT = TypeVar("RT")  # return type


def retry_error(
    max_retries: int = 3,
    backoff_in_seconds: int = 1,
    backoff_factor: int = 2,
) -> Callable[[Callable[[], RT]], Callable[[], RT]]:
    """
    Decorator takes arguments to adjust number of retries and backoff strategy.
    Args:
        max_retries (int): number of times to retry in case of failure.
        backoff_in_seconds (int): Number of seconds to sleep the first time through.
        backoff_factor (int): Value of the factor used for backoff.
    """

    def decorator_retry_error(func: Callable[[], RT]) -> Callable[[], RT]:
        """
        Main Decorator that takes our function as an argument
        """

        @functools.wraps(func)  # Use built in for decorators
        def wrapper_retry_error(*args, **kwargs) -> RT:
            """
            Wrapper that performs our extra tasks on the function
            """
            logger = None
            for arg in args:
                if isinstance(arg, Logger):
                    logger = arg
                    break
            # Initialize the retry loop
            total_retries = 0

            # Enter loop
            while True:
                # Try the function and catch the expected error
                # noinspection PyBroadException
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if total_retries == max_retries:
                        # Log it and re-raise if we maxed our retries + initial attempt
                        if logger is not None:
                            logger.error(
                                f"Encountered Errors {total_retries} times. "
                                f"Reached max retry limit.",
                            )
                        raise
                    else:
                        # perform exponential delay
                        backoff_time = (
                                backoff_in_seconds * backoff_factor ** total_retries
                                + random.uniform(0, 1)  # nosec
                        )
                        if logger is not None:
                            logger.error(
                                f"Encountered Error on attempt {total_retries}. "
                                f"Sleeping {backoff_time} seconds."
                            )
                        time.sleep(backoff_time)
                        total_retries += 1

        # Return our wrapper
        return wrapper_retry_error

    # Return our decorator
    return decorator_retry_error
