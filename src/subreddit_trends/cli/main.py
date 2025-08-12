import os

import typer

from subreddit_trends.cli import options
from subreddit_trends.cli.options import StorageBackend, TimeFilter
from subreddit_trends.reddit.reddit_scraper import RedditScraper
from subreddit_trends.storage.storage_backends import (LocalS3Storage,
                                                       LocalStorage)

app = typer.Typer()


@app.command()
def get_top_submissions(
    subreddit_name: str = options.subreddit_name,
    time_filter: TimeFilter = options.time_filter,
    limit: int = options.limit,
    verbose: bool = options.verbose,
    storage_backend: StorageBackend = options.storage_backend,
):
    """
    Retrieve the top submission(s) from a specified subreddit within a given time filter.
    """
    reddit_scraper = RedditScraper()
    result = reddit_scraper.get_top_submission(subreddit_name, time_filter, limit)

    if verbose:
        typer.echo(
            f"Retrieved {len(result.df)} top submission(s) from '{subreddit_name}' subreddit."
        )
        typer.echo(f"API Method: {result.api_method}")
        typer.echo(f"Time Filter: {result.time_filter}")
        typer.echo("These are the first rows of the DataFrame:")
        typer.echo(result.df)

    if storage_backend == "local":
        storage = LocalStorage()
    elif storage_backend == "minio":
        storage = LocalS3Storage(
            access_key=os.getenv("MINIO_ROOT_USER"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
            bucket=result.subreddit,
        )

    storage.save_parquet(result)


@app.command()
def hello_world():
    """
    A simple command to print 'Hello, World!'.
    """
    typer.echo("Hello, World!")


if __name__ == "__main__":
    app()
