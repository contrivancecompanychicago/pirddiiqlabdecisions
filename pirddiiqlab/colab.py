"""Helpers for running pirddiiqlab in Google Colab."""

import os


def is_colab() -> bool:
    """Return True when running inside a Google Colab runtime."""
    try:
        import sys

        return "google.colab" in sys.modules or os.path.exists("/content")
    except Exception:
        return False


def configure_colab_environment():
    """Apply safe defaults for Colab runtime behavior."""
    if not is_colab():
        return {
            "colab": False,
            "db_path": os.environ.get("PIRDDIIQLAB_DB_PATH", "pirddiiqlab_v0.db"),
            "host": os.environ.get("HOST", "0.0.0.0"),
            "port": os.environ.get("PORT", "8080"),
        }

    os.environ.setdefault("PIRDDIIQLAB_DB_PATH", "/content/pirddiiqlab_v0.db")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8080")

    return {
        "colab": True,
        "db_path": os.environ["PIRDDIIQLAB_DB_PATH"],
        "host": os.environ["HOST"],
        "port": os.environ["PORT"],
    }
