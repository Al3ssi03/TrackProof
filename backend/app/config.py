import os

DEFAULT_DATABASE_URL = "postgresql://trackproof:trackproof@localhost:5432/trackproof"


def database_url() -> str:
    return os.environ.get("TRACKPROOF_DATABASE_URL", DEFAULT_DATABASE_URL)
