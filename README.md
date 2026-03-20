q# subreddit-trends

A CLI tool for scraping Reddit submissions and storing them as Parquet files — either locally or in a MinIO (S3-compatible) backend. Built with [PRAW](https://praw.readthedocs.io/), [Typer](https://typer.tiangolo.com/), and Docker Compose.

---

## Features

- Fetch **top** or **hot** submissions from any subreddit
- Filter by time period (`hour`, `day`, `week`, `month`, `year`, `all`)
- Save results as **Parquet** files
- Two storage backends: **local filesystem** or **MinIO** (S3-compatible object storage)
- Verbose mode for quick inspection of results

---

## Project Structure

```
subreddit_trends/
├── cli/
│   ├── options.py          # Shared Typer CLI option definitions
│   └── commands.py         # CLI commands (get-top-submissions, etc.)
├── reddit/
│   └── reddit_scraper.py   # PRAW-based scraper (RedditScraper, ScrapeResult)
└── storage/
    └── storage_backends.py # LocalStorage and LocalS3Storage (MinIO)
```

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for MinIO)
- A Reddit API application — create one at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

---

## Installation

```bash
git clone https://github.com/your-org/subreddit-trends.git
cd subreddit-trends
uv sync
```

---

## Reddit API Configuration

This project uses PRAW's `praw.ini` file for credentials. Create a `praw.ini` in the project root (it is gitignored by default):

```ini
[subreddit_trends_bot1]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
user_agent=subreddit_trends_bot1 by u/YOUR_USERNAME
```

> The section name `subreddit_trends_bot1` must match the name passed to `praw.Reddit()` in `reddit_scraper.py`.

---

## Storage Backends

### Local

Saves Parquet files to `data/<subreddit>/<api_method>/` relative to the project root.

File naming: `<api_method>_<time_filter>_<timestamp>.parquet`

No additional setup required.

### MinIO (default)

MinIO is an S3-compatible object store that runs locally via Docker Compose. Object paths follow:

```
<subreddit>/<api_method>/<time_filter>/<timestamp>.parquet
```

#### Start MinIO

```bash
docker compose up -d
```

#### Environment Variables

Create a `.env` file in the project root:

```env
MINIO_ROOT_USER=your_access_key
MINIO_ROOT_PASSWORD=your_secret_key
```

MinIO will be available at `http://localhost:9000`. The web console is at `http://localhost:9001`.

---

## Usage

### `get-top-submissions`

Retrieve the top submission(s) from a subreddit.

```bash
python -m subreddit_trends.cli.commands get-top-submissions <SUBREDDIT> [OPTIONS]
```

**Arguments**

| Argument | Description |
|---|---|
| `SUBREDDIT` | Name of the subreddit to query (required) |

**Options**

| Option | Default | Description |
|---|---|---|
| `--time-filter` | `week` | Time period: `hour`, `day`, `week`, `month`, `year`, `all` |
| `--limit` | `1` | Number of submissions to retrieve |
| `--storage-backend` | `minio` | Storage backend: `minio` or `local` |
| `--verbose` / `-v` | `False` | Print results and metadata to stdout |

**Examples**

```bash
# Top post from r/streetphotography this week, saved to MinIO
subreddit_trends get-top-submissions streetphotography

# Top 5 posts from r/streetphotography this month, saved locally
subreddit_trends get-top-submissions streetphotography \
  --time-filter month \
  --limit 5 \
  --storage-backend local

# Fetch and print results without saving
subreddit_trends get-top-submissions streetphotography \
  --verbose
```

---

## Output Schema

Results are stored as Parquet files with the following columns:

| Column | Type | Description |
|---|---|---|
| `id` | `string` | Reddit post ID |
| `url` | `string` | URL of the post |
| `permalink` | `string` | Reddit permalink |
| `subreddit` | `string` | Subreddit name |
| `author` | `string` | Post author (nullable) |
| `title` | `string` | Post title |
| `created_utc` | `datetime64[ns]` | Post creation timestamp |
| `post_type` | `string` | `single_image`, `image_gallery`, or `other` |
| `score` | `int64` | Upvote score |
| `num_comments` | `int64` | Number of comments |
| `is_gallery` | `boolean` | Whether the post is a gallery |
| `num_of_images` | `int64` | Number of images (0 if not image post) |
| `upvote_ratio` | `float64` | Ratio of upvotes to total votes |


---

## Development

```bash
# Run tests
pytest

# Lint
ruff check .
```

---

## License

MIT
