# subreddit_trends/cli/utils.py

import socket
from subreddit_trends.exceptions import MinioNotAvailable


def check_minio_connection(host: str = "localhost", port: int = 9000, timeout: int = 2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except (ConnectionRefusedError, socket.timeout, OSError):
        raise MinioNotAvailable(
            f"Cannot reach MinIO at {host}:{port}. "
            "Is Docker running? Try: docker compose up -d"
        )
