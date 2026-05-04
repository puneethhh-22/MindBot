"""
response_builder.py
--------------------
Builds empathetic chatbot responses using Reddit posts as context.

This module REPLACES prompt_engine.py.
Instead of building LLM prompts, it:
  1. Detects user intent from keywords
  2. Formats Reddit posts into readable responses
  3. Appends CBT-based coping tips
  4. Applies response templates for consistent tone

Covers syllabus topics:
- Unit V: Prompt Engineering → Response Template Engineering
- Unit IV: NLP — intent detection, keyword extraction, text formatting
- Unit I: Domain-specific AI response generation
- Unit III: Rule-based reasoning (intent classification)
"""

import random
import re
from config import DomainConfig


class ResponseBuilder:
    """
    Builds structured, empathetic responses from Reddit API data.

    Architecture:
    ─────────────────────────────────────────────────────────
    User Message
        │
        ▼
    Intent Detection (keyword matching)
        │
        ▼
    Subreddit Selection (intent → subreddit map)
        │
        ▼
    Reddit Search (RedditClient.search_posts)
        │
        ▼
    Post Formatting (format_reddit_context)
        │
        ▼
    Coping Tip Selection (intent-matched CBT tip)
        │
        ▼
    Response Assembly (template + content + tip)
        │
        ▼
    Final Response String → UI
    """

    def __init__(self, domain: DomainConfig):
        self.domain = domain

    # ── Intent Detection ─────────────────────────────────────────────────────

    def detect_intent(self, user_message: str) -> str:
        """
        Detect the user's mental health intent from their message.

        Uses keyword matching (rule-based NLP — Unit III).
        Returns the best-matching intent category.

        Args:
            user_message: Raw user text

        Returns:
            Intent string (e.g. "anxiety", "depression", "general")
        """
        text = user_message.lower()
        scores = {}

        for intent, keywords in self.domain.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[intent] = score

        if not scores:
            return "general"

        # Return intent with most keyword matches
        return max(scores, key=scores.get)

    def get_search_query(self, user_message: str, intent: str) -> str:
        """
        Build a focused Reddit search query from user message + intent.

        Removes filler words and keeps emotionally relevant terms.

        Args:
            user_message: Raw user text
            intent:       Detected intent

        Returns:
            Clean search query string (max 8 words)
        """
        # Remove common filler words
        stopwords = {"i", "me", "my", "the", "a", "an", "is", "am", "are",
                     "was", "were", "be", "been", "have", "has", "had", "do",
                     "does", "did", "will", "would", "could", "should", "can",
                     "really", "just", "so", "very", "and", "but", "or", "to",
                     "of", "in", "on", "at", "for", "with", "it", "this", "that"}

        words = re.findall(r'\b[a-z]+\b', user_message.lower())
        filtered = [w for w in words if w not in stopwords and len(w) > 2]

        # Combine user words with intent keyword for better search precision
        if intent != "general" and intent not in filtered:
            filtered = [intent] + filtered

        query = " ".join(filtered[:8])
        return query if query else intent

    def get_subreddits_for_intent(self, intent: str) -> list:
        """
        Return the best subreddits to search for a given intent.

        Args:
            intent: Detected intent string

        Returns:
            List of subreddit names
        """
        return self.domain.intent_subreddit_map.get(intent, ["mentalhealth"])

    # ── Response Assembly ────────────────────────────────────────────────────

    def build_response(self, user_message: str, reddit_posts: list, intent: str) -> str:
        """
        Assemble the final chatbot response.

        Combines:
        - Formatted Reddit community posts (social proof + relatability)
        - Intent-matched CBT coping tip
        - Empathetic response template

        Args:
            user_message:  Original user input
            reddit_posts:  List of post dicts from RedditClient
            intent:        Detected intent

        Returns:
            Final response string for display to user
        """
        coping_tip = self._get_coping_tip(intent)

        if reddit_posts:
            reddit_content = self._format_reddit_context(reddit_posts)
            response = self.domain.response_templates["found_posts"].format(
                reddit_content=reddit_content,
                coping_tip=coping_tip,
            )
        else:
            response = self.domain.response_templates["no_posts"].format(
                coping_tip=coping_tip,
            )

        return response

    def build_fallback_response(self) -> str:
        """
        Return a fallback response when Reddit API is unavailable.

        Returns:
            Empathetic fallback string
        """
        return random.choice(self.domain.fallback_responses)

    # ── Formatting ───────────────────────────────────────────────────────────

    def _format_reddit_context(self, posts: list) -> str:
        """
        Format Reddit posts into readable, empathetic context blocks.

        Format per post:
        ────────────────
        📌 "Post Title" (r/subreddit · N upvotes)
           Body snippet...
           💬 Top comment: "..."

        Args:
            posts: List of post dicts from RedditClient

        Returns:
            Formatted multi-line string
        """
        lines = ["Here's what others in the community have shared:\n"]

        for i, post in enumerate(posts[:3], 1):  # Show max 3 posts
            title   = post.get("title", "")
            body    = post.get("body", "")
            score   = post.get("score", 0)
            comment = post.get("top_comment", "")
            sub     = post.get("subreddit", "mentalhealth")

            lines.append(f"📌 \"{title}\"")
            lines.append(f"   (r/{sub} · {score} upvotes)")

            if body:
                lines.append(f"   {body}")

            if comment:
                lines.append(f"   💬 Community response: \"{comment}\"")

            lines.append("")  # spacing between posts

        return "\n".join(lines).strip()

    def _get_coping_tip(self, intent: str) -> str:
        """
        Return a random CBT-based coping tip for the detected intent.

        Args:
            intent: Detected intent string

        Returns:
            Coping tip string
        """
        tips = self.domain.coping_tips.get(intent, self.domain.coping_tips["general"])
        return random.choice(tips)

    # ── Mood-Calibrated Opener ────────────────────────────────────────────────

    def get_mood_opener(self, mood_score: int) -> str:
        """
        Return an empathetic opener based on mood score.
        Mirrors the PromptEngine mood logic from the original project.

        Args:
            mood_score: Integer 1–10

        Returns:
            Opener string to prepend to response
        """
        if mood_score <= 3:
            return (
                f"A {mood_score}/10 tells me things feel really heavy right now, "
                "and I want you to know that's valid. You don't have to explain yourself or 'get better' quickly. "
                "I'm here, and I'm listening. 💙\n\n"
            )
        elif mood_score <= 6:
            return (
                f"A {mood_score}/10 — sounds like things are somewhere in the middle, "
                "which can feel unsettling in its own way. "
                "Let's see what might help you feel a little lighter. 💙\n\n"
            )
        else:
            return (
                f"A {mood_score}/10 — that's genuinely good to hear! "
                "Let's keep that momentum going. 🌟\n\n"
            )
