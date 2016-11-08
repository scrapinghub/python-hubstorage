"""
HubStorage client library
"""
__all__ = ["HubstorageClient"]

from .client import HubstorageClient, __version__
from .batchuploader import ValueTooLarge
import warnings


class HubstorageDeprecationWarning(Warning):
    """Warning subclass for the library, since the default
    DeprecationWarning is silenced on Python 2.7+
    """
    pass


DEPRECATION_MSG = (
    "python-hubstorage is deprecated, please use python-scrapinghub >= 1.9.0" +
    " instead (https://pypi.python.org/pypi/scrapinghub)."
)

warnings.warn(DEPRECATION_MSG, HubstorageDeprecationWarning, stacklevel=2)
