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


def launch_colab_app(host="0.0.0.0", port=8080, debug=False, db_path=None):
    """Launch the Flask app in a notebook-friendly Colab environment.

    Returns the app instance. In Colab, it also prints the public tunnel URL when
    a ngrok/Cloudflare tunnel is configured externally.
    """
    from .backend import create_app

    base_db_path = db_path or os.environ.get("PIRDDIIQLAB_DB_PATH")
    if base_db_path is None and is_colab():
        base_db_path = "/content/pirddiiqlab_v0.db"

    app = create_app(db_path=base_db_path)
    app.config["DEBUG"] = debug

    if is_colab():
        print("Colab environment detected.")
        print(f"SQLite DB: {base_db_path or 'default'}")
        print("Use a tunnel (for example ngrok or Cloudflare) to expose the app externally.")
        print("Example: app.run(host='0.0.0.0', port=8080)")

    return app
