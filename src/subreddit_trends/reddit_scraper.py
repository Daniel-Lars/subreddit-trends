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

    def _parse_submission(
        self, submissions, subreddit_name, api_method, time_filter=None, limit=1
    ) -> ScrapeResult:
        """
        Parses a list of Reddit submissions and extracts relevant information into a pandas DataFrame.
        Args:
            submissions (iterable): An iterable of Reddit submission objects.
            subreddit_name (str): The name of the subreddit from which submissions are scraped.
            api_method (str): The API method used to retrieve the submissions.
            time_filter (str, optional): The time filter applied to the API request (e.g., 'day', 'week').
            limit (int, optional): The maximum number of submissions to process. Defaults to 1.
        Returns:
            ScrapeResult: An object containing the resulting DataFrame and metadata about the scrape operation.
        Notes:
            - Determines post type (image gallery, single image, or other) and counts images accordingly.
            - Extracts fields such as id, url, author, title, score, number of comments, and upvote ratio.
            - Casts DataFrame columns to explicit types for consistency.
        """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = []

        for submission in submissions:
            # Calculate the number of images in the gallery if it is a gallery post
            # Otherwise, set it to 1 for single image posts
            # and handle other post types accordingly

            is_gallery = getattr(submission, "is_gallery", False)

            if is_gallery:
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
                    "is_gallery": is_gallery,
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
            api_method=api_method,
            subreddit=subreddit_name,
            time_filter=time_filter,
            timestamp=timestamp,
        )

    def get_top_submission(
        self, subreddit_name, time_filter="week", limit=1
    ) -> ScrapeResult:
        """
        Retrieve the top submission(s) from a specified subreddit within a given time filter.
        Args:
            subreddit_name (str): The name of the subreddit to query.
            time_filter (str, optional): The time period to consider for top submissions.
                Valid options are "all", "day", "hour", "month", "week", "year".
                Defaults to "week".
            limit (int, optional): The maximum number of top submissions to retrieve.
                Defaults to 1.
        Returns:
            ScrapeResult: The parsed result containing information about the top submission(s).
        Raises:
            prawcore.exceptions.NotFound: If the subreddit does not exist.
            prawcore.exceptions.Forbidden: If access to the subreddit is restricted.
            Exception: For other errors encountered during scraping.
        """

        submissions = self.reddit.subreddit(subreddit_name).top(
            time_filter=time_filter, limit=limit
        )

        return self._parse_submission(
            submissions=submissions,
            subreddit_name=subreddit_name,
            api_method="top",
            time_filter=time_filter,
        )

    def get_hot_submission(self, subreddit_name, limit=1) -> ScrapeResult:
        """
        Retrieves hot submissions from a specified subreddit.
        Args:
            subreddit_name (str): The name of the subreddit to fetch hot submissions from.
            limit (int, optional): The maximum number of submissions to retrieve. Defaults to 1.
        Returns:
            ScrapeResult: The parsed result containing information about the retrieved submissions.
        """

        submissions = self.reddit.subreddit(subreddit_name).hot(limit=limit)

        return self._parse_submission(
            submissions=submissions, subreddit_name=subreddit_name, api_method="hot"
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

        if result.time_filter is None:
            result.time_filter = "at_point_in_time"

        file_name = (
            f"{result.api_method}_{result.time_filter}_{result.timestamp}.parquet"
        )
        file_path = data_dir / file_name
        result.df.to_parquet(file_path, index=False)
        print(f"Data saved to {file_path}")
