"""
memory.py
---------
Conversation Memory Management for Mental Health Chatbot.

Covers syllabus topics:
- Unit IV: Context window management, NLP multi-turn dialogue
- Unit III: Sequential decision making (history-aware responses)
- Unit IV: Transformer Architecture (attention over conversation history)
"""

from datetime import datetime


class ConversationMemory:
    """
    Session-based conversation memory.

    Implements a sliding window approach:
    - Keeps the last `max_turns` exchanges in memory
    - Prevents context window overflow for the LLM
    - Stores timestamps for mood trend analysis

    Memory Type: Session-based (as per INT428 manual Q7)
    - Data is in-memory only (no database)
    - Cleared on reset or app restart
    """

    def __init__(self, max_turns: int = 10):
        """
        Initialize memory with a maximum turn limit.

        Args:
            max_turns: Maximum conversation turns to retain.
                       Beyond this, oldest turns are dropped (sliding window).
        """
        self.max_turns = max_turns
        self._history: list[tuple[str, str]] = []   # (user_msg, bot_msg)
        self._timestamps: list[str] = []
        self._mood_log: list[dict] = []
        self.turn_count: int = 0

    def add_turn(self, user_message: str, bot_response: str) -> None:
        """
        Add a conversation turn to memory.

        If history exceeds max_turns, oldest entry is removed (FIFO).

        Args:
            user_message: User's input text
            bot_response: Chatbot's response text
        """
        self._history.append((user_message, bot_response))
        self._timestamps.append(datetime.now().strftime("%H:%M:%S"))
        self.turn_count += 1

        # Sliding window: remove oldest turn if limit exceeded
        if len(self._history) > self.max_turns:
            self._history.pop(0)
            self._timestamps.pop(0)

    def get_history(self) -> list[tuple[str, str]]:
        """
        Return current conversation history.

        Returns:
            List of (user_message, bot_response) tuples
        """
        return self._history.copy()

    def log_mood(self, mood_score: int, note: str = "") -> None:
        """
        Log a mood entry for trend tracking.

        Args:
            mood_score: Integer 1-10
            note: Optional user note about their mood
        """
        entry = {
            "score": mood_score,
            "note": note,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self._mood_log.append(entry)

    def get_mood_trend(self) -> list[dict]:
        """
        Return all logged mood entries for this session.

        Returns:
            List of mood log dictionaries
        """
        return self._mood_log.copy()

    def get_mood_average(self) -> float | None:
        """
        Calculate average mood score for the session.

        Returns:
            Float average or None if no mood entries exist
        """
        if not self._mood_log:
            return None
        scores = [entry["score"] for entry in self._mood_log]
        return round(sum(scores) / len(scores), 2)

    def clear(self) -> None:
        """Reset all memory and statistics."""
        self._history.clear()
        self._timestamps.clear()
        self._mood_log.clear()
        self.turn_count = 0

    def get_last_exchange(self) -> tuple[str, str] | None:
        """
        Return the most recent (user, bot) exchange.

        Returns:
            Tuple of (user_message, bot_response) or None
        """
        if self._history:
            return self._history[-1]
        return None

    def __len__(self) -> int:
        return len(self._history)

    def __repr__(self) -> str:
        return f"ConversationMemory(turns={len(self._history)}, max={self.max_turns})"
