"""Module for handling errors in clients."""

import httpx

from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_exponential


def retry_on_http_error(function):
    """Decorate a function to retry on HTTPError."""
    function = retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_exponential(multiplier=1, min=3, max=5),
        stop=stop_after_delay(10),
        reraise=True,
    )(function)
    return function
