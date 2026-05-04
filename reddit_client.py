"""
reddit_client.py
----------------
Reddit API Client using PRAW (Python Reddit API Wrapper).

This module REPLACES the OpenAI API client entirely.
Instead of generating responses via LLM, it fetches real posts
and comments from mental health subreddits as knowledge context.

Covers syllabus topics:
- Unit VI: Working with external APIs and data pipelines
- Unit IV: NLP — information retrieval, text preprocessing
- Unit I: AI Applications — social data as AI knowledge source
- Unit VI: Unstructured data handling (Reddit posts = unstructured text)
"""

import os
import re
import random
from datetime import datetime, timedelta


class RedditClient:
    """
    Wrapper around PRAW (Python Reddit API Wrapper).

    Authentication Flow (OAuth2 - read-only):
    ─────────────────────────────────────────
    1. User registers app at reddit.com/prefs/apps → gets client_id + secret
    2. PRAW uses these to request an access token from Reddit OAuth2 server
    3. Token allows read-only access to public subreddits (no user login needed)
    4. Rate limit: 60 requests/minute (free, no billing)

    Data Retrieved:
    ───────────────
    - Post title + selftext (body)
    - Post score (upvotes)
    - Top comments (filtered for quality)
    - Post created timestamp
    """

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit API client.

        Args:
            client_id:     From reddit.com/prefs/apps
            client_secret: Secret key from Reddit app
            user_agent:    App identifier (e.g. "MindBot/1.0 INT428 Project")
        """
        try:
            import praw
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
            )
            # Verify connection by fetching Reddit frontpage title
            _ = self.reddit.subreddit("mentalhealth").id
            print("[RedditClient] Connected to Reddit API ✓")
            self.connected = True

        except ImportError:
            raise ImportError("PRAW not installed. Run: pip install praw")
        except Exception as e:
            print(f"[RedditClient] Warning: Could not connect — {e}")
            self.connected = False

    def search_posts(
        self,
        query: str,
        subreddits: list,
        max_posts: int = 5,
        min_upvotes: int = 10,
        time_filter: str = "year",
    ) -> list[dict]:
        """
        Search Reddit for posts matching a query across given subreddits.

        Process:
        1. For each subreddit, call Reddit Search API with the query
        2. Filter posts by minimum upvotes (quality gate)
        3. Filter out very short posts (low information)
        4. Extract title, body snippet, score, and top comment
        5. Return cleaned list of post dicts

        Args:
            query:       Search query string (e.g. "feeling anxious all the time")
            subreddits:  List of subreddit names to search
            max_posts:   Maximum number of posts to return
            min_upvotes: Minimum score threshold for quality filtering
            time_filter: Reddit time filter ("year", "month", "all", etc.)

        Returns:
            List of post dicts with keys: title, body, score, top_comment, subreddit
        """
        if not self.connected:
            return []

        results = []
        seen_titles = set()  # Deduplicate similar posts

        try:
            for subreddit_name in subreddits:
                if len(results) >= max_posts:
                    break

                subreddit = self.reddit.subreddit(subreddit_name)

                for post in subreddit.search(
                    query,
                    sort="relevance",
                    time_filter=time_filter,
                    limit=10,
                ):
                    if len(results) >= max_posts:
                        break

                    # ── Quality Filters ──────────────────────────────
                    if post.score < min_upvotes:
                        continue
                    if len(post.selftext) < 30:  # Skip empty posts
                        continue
                    if post.title in seen_titles:  # Skip duplicates
                        continue
                    if post.over_18:  # Skip NSFW
                        continue

                    seen_titles.add(post.title)

                    # ── Extract top comment ──────────────────────────
                    top_comment = self._get_top_comment(post)

                    # ── Clean and clip text ──────────────────────────
                    body_snippet = self._clean_text(post.selftext, max_chars=250)

                    results.append({
                        "title":       post.title,
                        "body":        body_snippet,
                        "score":       post.score,
                        "top_comment": top_comment,
                        "subreddit":   subreddit_name,
                        "url":         f"https://reddit.com{post.permalink}",
                    })

        except Exception as e:
            print(f"[RedditClient] Search error: {e}")

        return results

    def get_hot_posts(self, subreddit_name: str, limit: int = 3) -> list[dict]:
        """
        Fetch currently hot posts from a subreddit.
        Used for general mood support when no specific query matches.

        Args:
            subreddit_name: Name of subreddit
            limit:          Number of posts to return

        Returns:
            List of post dicts
        """
        if not self.connected:
            return []

        results = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            for post in subreddit.hot(limit=limit + 5):
                if post.stickied:  # Skip pinned mod posts
                    continue
                if len(post.selftext) < 30:
                    continue
                body_snippet = self._clean_text(post.selftext, max_chars=200)
                results.append({
                    "title":   post.title,
                    "body":    body_snippet,
                    "score":   post.score,
                    "subreddit": subreddit_name,
                })
                if len(results) >= limit:
                    break
        except Exception as e:
            print(f"[RedditClient] Hot posts error: {e}")

        return results

    def _get_top_comment(self, post, max_chars: int = 200) -> str:
        """
        Extract the highest-voted top-level comment from a post.

        Args:
            post:      PRAW Submission object
            max_chars: Maximum characters to return

        Returns:
            Cleaned comment string, or empty string if none found
        """
        try:
            post.comments.replace_more(limit=0)  # Expand only top-level comments
            top_comments = sorted(
                [c for c in post.comments.list()
                 if hasattr(c, 'score') and c.score > 5 and len(c.body) > 20],
                key=lambda c: c.score,
                reverse=True
            )
            if top_comments:
                return self._clean_text(top_comments[0].body, max_chars=max_chars)
        except Exception:
            pass
        return ""

    def _clean_text(self, text: str, max_chars: int = 300) -> str:
        """
        Clean Reddit post/comment text for display.

        Removes:
        - Reddit markdown formatting (**bold**, *italic*, etc.)
        - URLs
        - Excessive whitespace and newlines
        - Edit notices

        Args:
            text:      Raw Reddit text
            max_chars: Maximum characters to return

        Returns:
            Clean, readable string
        """
        if not text or text == "[deleted]" or text == "[removed]":
            return ""

        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove markdown formatting
        text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
        text = re.sub(r'#{1,6}\s', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
        # Remove edit notices
        text = re.sub(r'(?i)edit:.*', '', text)
        # Collapse whitespace
        text = re.sub(r'\n{2,}', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text).strip()

        # Clip to max_chars at a sentence boundary if possible
        if len(text) > max_chars:
            clipped = text[:max_chars]
            # Try to end at a sentence
            last_period = max(clipped.rfind('.'), clipped.rfind('!'), clipped.rfind('?'))
            if last_period > max_chars // 2:
                text = clipped[:last_period + 1]
            else:
                text = clipped.rstrip() + "..."

        return text
