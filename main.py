"""
Mental Health Support Chatbot — Reddit API Edition
INT428 - Foundations & Applications of AI

Entry Point: Run this file to start the chatbot.
Usage: python main.py

API: Reddit API via PRAW (free, no billing)
"""

from chatbot import MentalHealthChatbot
from ui import ChatUI


def main():
    print("=" * 60)
    print("   🧠 MindBot — Mental Health Support Chatbot")
    print("   INT428 Project | Powered by Reddit API")
    print("=" * 60)
    print()

    bot = MentalHealthChatbot()
    ui = ChatUI(bot)
    ui.run()


if __name__ == "__main__":
    main()
