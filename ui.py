"""
ui.py
-----
Command-Line Interface for the Reddit-powered Mental Health Chatbot.

Changes from original:
- Removed model config display (temperature/top-p — no LLM)
- Added Reddit search status indicator
- Added /reddit command to show which subreddits are active
- Session summary shows Reddit API stats instead of model params

Covers syllabus topics:
- Unit I: Applications of AI (interactive AI system)
- Unit V: Responsible AI (crisis handling, ethical interaction)
- Unit VI: API data display and user interaction
"""

from chatbot import MentalHealthChatbot


class ChatUI:
    """Terminal-based Chat Interface for Reddit-powered MindBot."""

    COLORS = {
        "bot":     "\033[94m",   # Blue  → Bot messages
        "user":    "\033[92m",   # Green → User messages
        "system":  "\033[93m",   # Yellow → System messages
        "error":   "\033[91m",   # Red → Errors / crisis
        "reddit":  "\033[95m",   # Magenta → Reddit info
        "reset":   "\033[0m",
        "bold":    "\033[1m",
    }

    COMMANDS = {
        "/help":    "Show all available commands",
        "/mood":    "Log your current mood (1-10 scale)",
        "/journal": "Get a journaling prompt to reflect on your feelings",
        "/reddit":  "Show active subreddits and connection status",
        "/reset":   "Clear conversation history and start fresh",
        "/summary": "See your session summary",
        "/quit":    "Exit the chatbot",
    }

    JOURNAL_PROMPTS = [
        "What's one thing that made you feel something strongly today?",
        "Describe your current emotional state in 3 words. What caused it?",
        "What's been weighing on your mind lately? Write freely for 5 minutes.",
        "What's one thing you're grateful for today, even if small?",
        "If your emotions right now were weather, what would the forecast be?",
        "Write about a moment today where you felt at peace, even briefly.",
        "What would you say to a friend going through what you're experiencing?",
    ]

    def __init__(self, bot: MentalHealthChatbot):
        self.bot = bot
        self._journal_index = 0

    def run(self) -> None:
        """Main interaction loop."""
        self._print_welcome()

        while True:
            try:
                user_input = input(
                    f"{self.COLORS['user']}You: {self.COLORS['reset']}"
                ).strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    should_continue = self._handle_command(user_input.lower())
                    if not should_continue:
                        break
                    continue

                # Regular chat — show search indicator
                intent = self.bot.response_builder.detect_intent(user_input)
                subreddits = self.bot.response_builder.get_subreddits_for_intent(intent)
                print(f"{self.COLORS['reddit']}[Searching r/{', r/'.join(subreddits[:2])} for '{intent}' posts...]{self.COLORS['reset']}")

                response = self.bot.chat(user_input)
                print(f"\n{self.COLORS['bot']}🤖 MindBot: {self.COLORS['reset']}{response}\n")

            except KeyboardInterrupt:
                print("\n")
                self._print_goodbye()
                break

    def _handle_command(self, command: str) -> bool:
        if command == "/quit":
            self._print_goodbye()
            return False
        elif command == "/help":
            self._print_help()
        elif command == "/mood":
            self._mood_checkin()
        elif command == "/journal":
            self._journal_prompt()
        elif command == "/reddit":
            self._show_reddit_status()
        elif command == "/reset":
            self.bot.reset_memory()
            self._print_system("Memory cleared! Starting fresh conversation. 🌱")
        elif command == "/summary":
            self._print_summary()
        else:
            self._print_system(f"Unknown command: '{command}'. Type /help for available commands.")
        return True

    def _mood_checkin(self) -> None:
        """Interactive mood check-in (1-10 scale)."""
        self._print_system("📊 Mood Check-In")
        print("  Rate your current mood from 1 to 10:")
        print("  1 = Very low / struggling badly")
        print("  5 = Okay / neutral")
        print(" 10 = Great / feeling good\n")

        try:
            score = int(input("  Your mood score: ").strip())
            if not 1 <= score <= 10:
                self._print_system("Please enter a number between 1 and 10.")
                return

            note = input("  Optional — what's contributing to this mood? (press Enter to skip): ").strip()
            self.bot.memory.log_mood(score, note)

            # Build mood-contextual message and chat
            mood_opener = self.bot.response_builder.get_mood_opener(score)
            full_prompt = f"[Mood score: {score}/10] {note if note else 'No additional note.'}"
            response = self.bot.chat(full_prompt)
            print(f"\n{self.COLORS['bot']}🤖 MindBot: {self.COLORS['reset']}{mood_opener}{response}\n")

        except ValueError:
            self._print_system("Invalid input. Please enter a number between 1 and 10.")

    def _journal_prompt(self) -> None:
        """Display a rotating journaling prompt."""
        prompt = self.JOURNAL_PROMPTS[self._journal_index % len(self.JOURNAL_PROMPTS)]
        self._journal_index += 1
        self._print_system("📔 Journaling Prompt")
        print(f"\n  ✍️  {prompt}\n")
        print("  Take your time. You can share what you write here, or keep it private.\n")

    def _show_reddit_status(self) -> None:
        """Show Reddit API connection status and active subreddits."""
        summary = self.bot.get_session_summary()
        connected = summary["connected"]
        status = "✅ Connected" if connected else "❌ Not connected"

        self._print_system(f"Reddit API Status: {status}")
        print(f"  Active subreddits:")
        for sub in summary["subreddits"]:
            print(f"    • r/{sub}")
        print(f"  Max posts per query : {summary['max_posts']}")
        print(f"  Fallback responses  : {summary['fallbacks']}")
        print()

    def _print_summary(self) -> None:
        """Display session statistics."""
        summary = self.bot.get_session_summary()
        mood_avg = self.bot.memory.get_mood_average()
        mood_log = self.bot.memory.get_mood_trend()

        self._print_system("📋 Session Summary")
        print(f"  🔄 Total conversation turns : {summary['total_turns']}")
        print(f"  🌐 API                      : {summary['api']}")
        print(f"  📡 Reddit connected         : {'Yes' if summary['connected'] else 'No (fallback mode)'}")
        print(f"  📦 Max posts per query      : {summary['max_posts']}")

        if mood_log:
            print(f"\n  Mood Log ({len(mood_log)} entries):")
            for i, entry in enumerate(mood_log, 1):
                bar = "█" * entry["score"] + "░" * (10 - entry["score"])
                print(f"    [{i}] {entry['time']} | {bar} {entry['score']}/10 | {entry['note'] or '-'}")
            print(f"\n  Average mood this session: {mood_avg}/10")
        else:
            print("\n  No mood entries. Try /mood to log your mood!")
        print()

    def _print_welcome(self) -> None:
        print(f"{self.COLORS['bot']}")
        print("┌─────────────────────────────────────────────────────┐")
        print("│        🧠  MindBot — Mental Health Support          │")
        print("│            Powered by Reddit Community              │")
        print("│                                                     │")
        print("│  Hi! I'm MindBot. I search real mental health       │")
        print("│  communities to share relatable experiences and     │")
        print("│  evidence-based coping strategies with you.         │")
        print("│                                                     │")
        print("│  ⚠️  I am NOT a licensed therapist. For serious      │")
        print("│     concerns, please see a professional.            │")
        print("│                                                     │")
        print("│  Type /help to see available commands.              │")
        print("└─────────────────────────────────────────────────────┘")
        print(f"{self.COLORS['reset']}")
        print(f"{self.COLORS['bot']}🤖 MindBot: {self.COLORS['reset']}Hello! I'm so glad you're here. 💙")
        print("How are you feeling today? You can tell me anything — this is a safe space.\n")

    def _print_goodbye(self) -> None:
        self._print_summary()
        print(f"{self.COLORS['bot']}🤖 MindBot: {self.COLORS['reset']}")
        print("  Take care of yourself. Reaching out is always a sign of strength.")
        print("  🆘 iCall India: 9152987821 | Vandrevala: 1860-2662-345\n")

    def _print_help(self) -> None:
        self._print_system("Available Commands")
        for cmd, desc in self.COMMANDS.items():
            print(f"  {self.COLORS['bold']}{cmd:<12}{self.COLORS['reset']} — {desc}")
        print()

    def _print_system(self, message: str) -> None:
        print(f"\n{self.COLORS['system']}[System] {message}{self.COLORS['reset']}\n")
