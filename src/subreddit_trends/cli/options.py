from enum import Enum

import typer


class TimeFilter(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class StorageBackend(str, Enum):
    MINIO = "minio"
    LOCAL = "local"


subreddit_name: str = typer.Argument(..., help="Name of the subreddit to query")
time_filter: TimeFilter = typer.Option(
    TimeFilter.WEEK,
    help="Time period for subreddit submissions",
)
limit: int = typer.Option(
    1, help="Maximum number of submissions to retrieve from API call"
)
save: bool = typer.Option(False, "--save", "-s", help="Save the results to a file")
verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose execution")
storage_backend: StorageBackend = typer.Option(
    StorageBackend.MINIO, help="Storage backend: minio(default) or local path"
)
