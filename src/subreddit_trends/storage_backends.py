import io
import pathlib
from abc import ABC, abstractmethod

from minio import Minio

from subreddit_trends.reddit_scraper import ScrapeResult


# abstract class to define expected behaviour for storage class
class StorageBackend(ABC):
    @abstractmethod
    def save_parquet(self, result: ScrapeResult):
        pass


class LocalStorage(StorageBackend):
    """Class to handle saving data to a specified storage backend."""

    def save_parquet(self, result: ScrapeResult):
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


class LocalS3Storage(StorageBackend):
    def __init__(self, access_key, secret_key, bucket):
        self.client = Minio(
            "localhost:9000", access_key=access_key, secret_key=secret_key, secure=False
        )
        self.bucket = bucket
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        else:
            print(f"Bucket {self.bucket} already exists.")

    def save_parquet(self, result: ScrapeResult):
        buffer = io.BytesIO()
        result.df.to_parquet(buffer, index=False)
        buffer.seek(0)

        self.client.put_object(
            self.bucket,
            object_name=f"{result.subreddit}/{result.api_method}/{result.time_filter}/{result.timestamp}.parquet",
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type="application/octet-stream",
        )
