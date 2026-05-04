"""
config.py
---------
Configuration for Reddit-powered Mental Health Support Chatbot.

Covers syllabus topics:
- Unit V: Prompt Engineering - domain constraints, response patterns
- Unit IV: NLP, information retrieval from social platforms
- Unit I: Responsible AI, domain-aware AI, healthcare application
- Unit VI: Working with external APIs and data pipelines
"""


class RedditConfig:
    """
    Reddit API Configuration.

    How Reddit API works (for report):
    -----------------------------------
    Reddit provides a free REST API accessible via PRAW (Python Reddit API Wrapper).
    It allows reading public posts and comments from any subreddit.

    Authentication uses OAuth2 with:
        - client_id     : From your Reddit app (reddit.com/prefs/apps)
        - client_secret : Secret key from your Reddit app
        - user_agent    : Identifier string for your app (any descriptive name)

    Read-only mode: We use read-only access — no login required.
    Rate limit: 60 requests/minute (free, no billing ever).

    Subreddits used (mental health communities):
        - r/mentalhealth       : General mental health support
        - r/anxiety            : Anxiety-specific discussions
        - r/depression         : Depression support community
        - r/stress             : Stress and burnout discussions
        - r/sleep              : Sleep issues and insomnia
        - r/mindfulness        : Mindfulness and meditation
        - r/selfimprovement    : Coping strategies and growth
    """

    # ── Reddit OAuth2 Credentials ───────────────────────────────────────────
    # Fill these after creating your app at: https://www.reddit.com/prefs/apps
    # Leave as None — app reads from environment variables (see README)
    client_id:     str = None   # set env: REDDIT_CLIENT_ID
    client_secret: str = None   # set env: REDDIT_CLIENT_SECRET
    user_agent:    str = "MindBot/1.0 (INT428 AI Project; Mental Health Support Chatbot)"

    # ── Search Configuration ────────────────────────────────────────────────
    # Subreddits to search for relevant posts
    subreddits: list = [
        "mentalhealth",
        "anxiety",
        "depression",
        "stress",
        "sleep",
        "mindfulness",
        "selfimprovement",
    ]

    # Number of Reddit posts to fetch per query
    max_posts: int = 5

    # Minimum upvotes for a post to be considered (quality filter)
    min_upvotes: int = 10

    # Maximum age of posts in days (recency filter)
    max_age_days: int = 365

    # Sort method: "relevance", "hot", "top", "new"
    sort_method: str = "relevance"

    # Time filter for search: "all", "year", "month", "week", "day"
    time_filter: str = "year"


class DomainConfig:
    """
    Mental Health Domain Knowledge Configuration.

    Covers:
    - Unit V: Prompt patterns, response templates
    - Unit I: Healthcare domain rules and constraints
    - Unit VI: Domain data curation from trusted community sources
    """

    domain_name: str = "Mental Health Support"

    # ── Intent → Subreddit Mapping ──────────────────────────────────────────
    # Maps detected user intent to the most relevant subreddit
    intent_subreddit_map: dict = {
        "anxiety":      ["anxiety", "mentalhealth"],
        "depression":   ["depression", "mentalhealth"],
        "stress":       ["stress", "mentalhealth"],
        "sleep":        ["sleep", "mentalhealth"],
        "breathing":    ["mindfulness", "anxiety"],
        "loneliness":   ["mentalhealth", "depression"],
        "motivation":   ["selfimprovement", "mentalhealth"],
        "mindfulness":  ["mindfulness", "selfimprovement"],
        "general":      ["mentalhealth"],
    }

    # ── Intent Keywords ─────────────────────────────────────────────────────
    # Used to detect what the user is talking about
    intent_keywords: dict = {
        "anxiety":    ["anxious", "anxiety", "panic", "worry", "worried", "nervous", "fear", "scared"],
        "depression": ["depressed", "depression", "sad", "hopeless", "empty", "numb", "worthless"],
        "stress":     ["stressed", "stress", "overwhelmed", "pressure", "burnout", "exhausted"],
        "sleep":      ["sleep", "insomnia", "tired", "awake", "nighttime", "cant sleep", "rest"],
        "breathing":  ["breathe", "breathing", "breath", "inhale", "exhale", "calm down"],
        "loneliness": ["alone", "lonely", "isolated", "no friends", "no one understands"],
        "motivation": ["unmotivated", "lazy", "procrastinat", "can't start", "no energy"],
        "mindfulness": ["mindful", "meditat", "present", "grounded", "peace", "calm"],
    }

    # ── Response Templates (replaces LLM - Unit V Prompt patterns) ──────────
    # These templates structure the Reddit data into empathetic responses
    response_templates: dict = {
        "found_posts": (
            "I hear you, and I want you to know you're not alone. 💙\n\n"
            "I searched our mental health community and found what others have shared "
            "about similar experiences:\n\n"
            "{reddit_content}\n\n"
            "{coping_tip}\n\n"
            "Would you like to talk more about what you're going through?"
        ),
        "no_posts": (
            "I hear you, and I want you to know you're not alone. 💙\n\n"
            "{coping_tip}\n\n"
            "Remember — reaching out is always a sign of strength. "
            "Would you like to share more about what's been going on?"
        ),
        "general": (
            "Thank you for sharing that with me. 💙\n\n"
            "{reddit_content}\n\n"
            "You don't have to face this alone. Is there anything specific "
            "you'd like to explore or talk through?"
        ),
    }

    # ── Coping Tips Library (CBT-based, shown alongside Reddit content) ──────
    coping_tips: dict = {
        "anxiety": [
            "💡 Try the 4-4-6 breathing technique: inhale for 4 counts, hold for 4, exhale slowly for 6. This activates your parasympathetic nervous system and reduces panic.",
            "💡 Ground yourself with the 5-4-3-2-1 method: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "💡 Challenge anxious thoughts: ask yourself 'Is this thought a fact or a feeling? What's the most likely outcome?'",
        ],
        "depression": [
            "💡 Even a 10-minute walk outside can shift your mood — sunlight and movement are natural mood boosters backed by research.",
            "💡 Try 'behavioral activation': do one small enjoyable activity today, even if you don't feel like it. Action often comes before motivation, not after.",
            "💡 Write down 3 things, no matter how small, that went okay today. This gently trains your brain to notice positives.",
        ],
        "stress": [
            "💡 Try the 'brain dump' technique: write down everything on your mind for 5 minutes without filtering. Getting it out of your head reduces mental load.",
            "💡 Break overwhelming tasks into the smallest possible next step. Instead of 'study for exam', make it 'open the notebook'. Just the first step.",
            "💡 Set a 5-minute timer and do nothing but breathe. Stress feeds on constant action — intentional pauses are powerful.",
        ],
        "sleep": [
            "💡 'Cognitive offloading' before bed: write down tomorrow's to-do list. This tells your brain it's safe to stop processing and helps you fall asleep faster.",
            "💡 Keep your phone out of reach 30 minutes before bed. The blue light suppresses melatonin and keeps your brain alert.",
            "💡 Try progressive muscle relaxation: tense and release each muscle group from toes to head. This physically signals your body to rest.",
        ],
        "general": [
            "💡 Remember: emotions are temporary visitors, not permanent residents. What you're feeling right now will shift.",
            "💡 Self-compassion matters: speak to yourself the way you'd speak to a friend going through the same thing.",
            "💡 Small steps count. You don't need to solve everything today — just take the next tiny step forward.",
        ],
    }

    # ── Crisis Keywords (Responsible AI — Unit V Ethics) ────────────────────
    crisis_keywords: list = [
        "suicide", "suicidal", "kill myself", "end my life",
        "self harm", "self-harm", "hurt myself", "want to die",
        "not worth living", "no reason to live",
    ]

    # ── Crisis Response ──────────────────────────────────────────────────────
    crisis_response: str = """I'm really concerned about what you just shared, and I want you to know that you matter deeply. 💙

Please reach out to these crisis helplines immediately — they are free, confidential, and available 24/7:

🆘 iCall (India): 9152987821
🆘 Vandrevala Foundation: 1860-2662-345
🆘 AASRA: 98204 66627

If you are in immediate danger, please call 112 (Emergency) or go to your nearest hospital.

You don't have to face this alone. Would you like to talk about what's going on?"""

    # ── Fallback responses when Reddit is unavailable ────────────────────────
    fallback_responses: list = [
        "I'm here to listen. While I couldn't fetch community insights right now, I want you to know that what you're feeling is valid. Could you tell me more about what's going on?",
        "Connection issues aside — your feelings matter. Many people experience what you're describing. Would you like to try a quick coping technique together?",
        "I'm with you. Sometimes just expressing what you feel is the first step. Can you describe what's been happening for you lately?",
    ]
