import praw
from datetime import datetime
import pandas as pd 

class RedditScraper:
    
    def __init__(self):
        self.reddit = praw.Reddit("subreddit_trends_bot1")
        
    def get_top_submission(self, subreddit_name, time_filter='week', limit=1)-> pd.DataFrame:
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
        
        data = []
        
        for submission in self.reddit.subreddit(subreddit_name).top(time_filter=time_filter, limit=limit):
            
            # Calculate the number of images in the gallery if it is a gallery post
            # Otherwise, set it to 1 for single image posts
            # and handle other post types accordingly
            if getattr(submission, "is_gallery", False):
                post_type = 'image_gallery'
                num_of_images = len(getattr(submission, "gallery_data", {}).get("items", []))
            elif getattr(submission, "post_hint", "") == 'image':
                post_type = 'single_image'
                num_of_images = 1
            else:
                post_type = 'other'
                num_of_images = 0
                
            data.append({
                
                'id': submission.id,
                'url': submission.url,
                'permalink': submission.permalink,
                'subreddit': submission.subreddit.display_name,
                'author': submission.author.name if submission.author else None,
                'title': submission.title,
                'created_utc': datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                'post_type': post_type, 
                'score': submission.score,
                'num_comments': submission.num_comments,
                'is_gallery': submission.is_gallery,
                'num_of_images': num_of_images,
                'upvote_ratio': submission.upvote_ratio,
            })
            
        
        return pd.DataFrame(data)
        

        
        
        