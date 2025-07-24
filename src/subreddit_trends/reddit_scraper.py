import pathlib
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import praw


@dataclass
class ScrapeResult:
    df: pd.DataFrame
    api_method: str  # API method used for scraping e.g. "top", "hot", etc.
    subreddit: str  # subreddit name
    time_filter: str  # applied time filter
    timestamp: str  # timestamp of the scrape operation


class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit("subreddit_trends_bot1")

    def get_top_submission(
        self, subreddit_name, time_filter="week", limit=1
    ) -> ScrapeResult:
        """Fetches the top submission(s) from a specified subreddit within a given time filter.
        Parameters:
            subreddit_name (str): Name of the subreddit to fetch submissions from.
            time_filter (str, optional): Time period to consider for top submissions.
                Valid values are 'all', 'day', 'hour', 'month', 'week', 'year'. Defaults to 'week'.
            limit (int, optional): Number of top submissions to fetch. Defaults to 1.
        Returns:
            pandas.DataFrame: A DataFrame containing information about the top submission(s), including:
                - id: Submission ID
                - url: URL of the submission
                - permalink: Reddit permalink to the submission
                - subreddit: Name of the subreddit
                - author: Username of the author (None if deleted)
                - title: Title of the submission
                - created_utc: Submission creation time (UTC, formatted as "%Y-%m-%d %H:%M:%S")
                - post_type: Type of post ('image_gallery', 'single_image', or 'other')
                - score: Submission score (upvotes - downvotes)
                - num_comments: Number of comments
                - is_gallery: Boolean indicating if the post is a gallery
                - num_of_images: Number of images in the post (0 for non-image posts)
                - upvote_ratio: Upvote ratio of the submission
        """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = []

        for submission in self.reddit.subreddit(subreddit_name).top(
            time_filter=time_filter, limit=limit
        ):
            # Calculate the number of images in the gallery if it is a gallery post
            # Otherwise, set it to 1 for single image posts
            # and handle other post types accordingly
            if getattr(submission, "is_gallery", False):
                post_type = "image_gallery"
                num_of_images = len(
                    getattr(submission, "gallery_data", {}).get("items", [])
                )
            elif getattr(submission, "post_hint", "") == "image":
                post_type = "single_image"
                num_of_images = 1
            else:
                post_type = "other"
                num_of_images = 0

            data.append(
                {
                    "id": submission.id,
                    "url": submission.url,
                    "permalink": submission.permalink,
                    "subreddit": submission.subreddit.display_name,
                    "author": submission.author.name if submission.author else None,
                    "title": submission.title,
                    "created_utc": datetime.fromtimestamp(
                        submission.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "post_type": post_type,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "is_gallery": submission.is_gallery,
                    "num_of_images": num_of_images,
                    "upvote_ratio": submission.upvote_ratio,
                }
            )

            df = pd.DataFrame(data)

            # Explicit type casting
            df = df.astype(
                {
                    "id": "string",
                    "url": "string",
                    "permalink": "string",
                    "subreddit": "string",
                    "author": "string",
                    "title": "string",
                    "created_utc": "datetime64[ns]",
                    "post_type": "string",
                    "score": "int64",
                    "num_comments": "int64",
                    "is_gallery": "boolean",
                    "num_of_images": "int64",
                    "upvote_ratio": "float64",
                }
            )

        return ScrapeResult(
            df=df,
            api_method="top",
            subreddit=subreddit_name,
            time_filter=time_filter,
            timestamp=timestamp,
        )


class DataSaver:
    """Class to handle saving data to a specified storage backend."""

    def save_local_parquet(self, result: ScrapeResult):
        """Saves the DataFrame to a local parquet file."""

        if result.df.empty:
            raise ValueError("DataFrame is empty. No data to save.")

        base_dir = pathlib.Path(__file__).resolve().parents[2]
        data_dir = base_dir / "data" / result.subreddit / result.api_method
        data_dir.mkdir(parents=True, exist_ok=True)

        file_name = (
            f"{result.api_method}_{result.time_filter}_{result.timestamp}.parquet"
        )
        file_path = data_dir / file_name
        result.df.to_parquet(file_path, index=False)
        print(f"Data saved to {file_path}")
