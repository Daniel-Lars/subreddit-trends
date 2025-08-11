import typer

from subreddit_trends.reddit_scraper import RedditScraper
from subreddit_trends.storage_backends import LocalS3Storage, LocalStorage

app = typer.Typer()


@app.command()
def get_top_submissions(
    subreddit_name: str = typer.Argument(..., help="Name of the subreddit to query"),
    time_filter: str = typer.Option("week", help="Time period for top submissions"),
    limit: int = typer.Option(1, help="Maximum number of top submissions to retrieve"),
    save: bool = typer.Option(False, "--save", "-s", help="Save the results to a file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose execution"),
    backend: str = typer.Option("local", help="Storage backend: local or minio"),
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
        typer.echo(result.df.head(5))

    if save:
        if backend == "local":
            storage = LocalStorage()
        elif backend == "minio":
            storage = LocalS3Storage(
                access_key="minioadmin",
                secret_key="minioadmin",
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
