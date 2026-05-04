"""
chatbot.py
----------
Core chatbot engine for Reddit-powered Mental Health Support Bot.

CHANGE FROM ORIGINAL:
  OpenAI GPT API  →  Reddit API (PRAW)
  LLM generation  →  Community post retrieval + template responses

Covers syllabus topics:
- Unit IV: Building chatbots and digital assistants
- Unit IV: NLP — intent detection, information retrieval
- Unit V: Response template engineering (replaces prompt engineering)
- Unit VI: External API integration, data pipelines
- Unit I: Applications in healthcare domain, Responsible AI
"""

import os
import random
from config import RedditConfig, DomainConfig
from memory import ConversationMemory
from reddit_client import RedditClient
from response_builder import ResponseBuilder


class MentalHealthChatbot:
    """
    Reddit-Powered Mental Health Support Chatbot.

    Architecture:
    ─────────────────────────────────────────────────────
    User Input
        │
        ▼
    Crisis Detection (config.py crisis_keywords)
        │
        ├─ YES → Return helpline response immediately
        │
        └─ NO  ▼
    Intent Detection (response_builder.detect_intent)
        │
        ▼
    Reddit Search (reddit_client.search_posts)
        │
        ▼
    Response Assembly (response_builder.build_response)
        │
        ▼
    Memory Storage (memory.add_turn)
        │
        ▼
    Output to UI

    Key Difference from LLM-based approach:
    - No API costs — Reddit API is completely free
    - Responses grounded in real community experiences
    - No hallucination — all content comes from real posts
    - Requires internet connection to fetch posts
    """

    def __init__(self):
        self.reddit_config = RedditConfig()
        self.domain = DomainConfig()
        self.memory = ConversationMemory(max_turns=10)
        self.response_builder = ResponseBuilder(self.domain)
        self.reddit = self._initialize_reddit_client()
        self._fallback_count = 0

        print("[MindBot] Initialized | Powered by: Reddit API (PRAW)")
        print(f"[MindBot] Subreddits: {', '.join(self.reddit_config.subreddits[:4])}...")
        print(f"[MindBot] Max posts per query: {self.reddit_config.max_posts}")

    def _initialize_reddit_client(self) -> RedditClient:
        """
        Initialize Reddit API client using credentials from environment variables.

        Environment variables required:
            REDDIT_CLIENT_ID      - From reddit.com/prefs/apps
            REDDIT_CLIENT_SECRET  - Secret key from Reddit app

        Returns:
            Initialized RedditClient instance
        """
        client_id = os.getenv("REDDIT_CLIENT_ID") or self.reddit_config.client_id
        client_secret = os.getenv("REDDIT_CLIENT_SECRET") or self.reddit_config.client_secret

        if not client_id or not client_secret:
            raise EnvironmentError(
                "\n❌ Reddit API credentials not set!\n\n"
                "Steps to fix:\n"
                "  1. Go to https://www.reddit.com/prefs/apps\n"
                "  2. Click 'Create App' → select 'script'\n"
                "  3. Copy client_id and client_secret\n"
                "  4. Set environment variables:\n\n"
                "  Windows:\n"
                "    set REDDIT_CLIENT_ID=your_id_here\n"
                "    set REDDIT_CLIENT_SECRET=your_secret_here\n\n"
                "  Mac/Linux:\n"
                "    export REDDIT_CLIENT_ID=your_id_here\n"
                "    export REDDIT_CLIENT_SECRET=your_secret_here\n"
            )

        return RedditClient(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=self.reddit_config.user_agent,
        )

    def chat(self, user_message: str) -> str:
        """
        Process user message and return chatbot response.

        Steps:
        1. Crisis keyword detection (safety — no API call needed)
        2. Intent detection from user message
        3. Build Reddit search query
        4. Fetch relevant Reddit posts
        5. Assemble empathetic response with coping tip
        6. Store in conversation memory
        7. Return response

        Args:
            user_message: Raw user input text

        Returns:
            Chatbot response string
        """
        # Step 1: Crisis detection — bypass everything, respond immediately
        if self._is_crisis(user_message):
            return self.domain.crisis_response

        # Step 2: Detect intent from user message (NLP - Unit IV)
        intent = self.response_builder.detect_intent(user_message)

        # Step 3: Build Reddit search query (keyword extraction)
        query = self.response_builder.get_search_query(user_message, intent)

        # Step 4: Select subreddits for this intent
        subreddits = self.response_builder.get_subreddits_for_intent(intent)

        # Step 5: Fetch Reddit posts (External API call - Unit VI)
        reddit_posts = []
        if self.reddit.connected:
            try:
                reddit_posts = self.reddit.search_posts(
                    query=query,
                    subreddits=subreddits,
                    max_posts=self.reddit_config.max_posts,
                    min_upvotes=self.reddit_config.min_upvotes,
                    time_filter=self.reddit_config.time_filter,
                )
            except Exception as e:
                print(f"[MindBot] Reddit fetch failed: {e}")

        # Step 6: Build response from Reddit content
        if reddit_posts:
            bot_reply = self.response_builder.build_response(
                user_message=user_message,
                reddit_posts=reddit_posts,
                intent=intent,
            )
        elif self.reddit.connected:
            # Connected but no posts found for this query
            bot_reply = self.response_builder.build_response(
                user_message=user_message,
                reddit_posts=[],
                intent=intent,
            )
        else:
            # Reddit not available — use fallback
            bot_reply = self.response_builder.build_fallback_response()
            self._fallback_count += 1

        # Step 7: Store turn in memory (context window - Unit IV)
        self.memory.add_turn(user_message, bot_reply)

        return bot_reply

    def _is_crisis(self, text: str) -> bool:
        """
        Detect crisis keywords in user input.
        Responsible AI (Unit V: Ethics & Responsible AI).

        This runs BEFORE any API call — safety first.
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.domain.crisis_keywords)

    def reset_memory(self):
        """Clear conversation history and start fresh session."""
        self.memory.clear()
        print("[MindBot] Memory cleared. Starting new session.")

    def get_session_summary(self) -> dict:
        """Return session statistics."""
        return {
            "total_turns":  self.memory.turn_count,
            "api":          "Reddit API (PRAW)",
            "subreddits":   self.reddit_config.subreddits,
            "max_posts":    self.reddit_config.max_posts,
            "connected":    self.reddit.connected,
            "fallbacks":    self._fallback_count,
        }
