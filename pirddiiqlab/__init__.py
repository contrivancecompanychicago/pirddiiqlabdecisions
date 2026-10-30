"""pirddiiqlab package export."""

from .backend import create_app
from .init import __version__

__all__ = ["create_app", "__version__"]
