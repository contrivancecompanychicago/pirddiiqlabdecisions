"""
pirddiiqlab package.

This package exposes the Flask app factory and package metadata so the
project can be imported cleanly after installation.
"""

from .backend import create_app

__version__ = "0.1.0"
__author__ = "make-DEEP-Human-Families-Healthy"

__all__ = ["create_app", "__version__", "__author__"]
