"""
streamlit_app.py
----------------
Web UI for the Reddit-powered Mental Health Chatbot.

Run with: streamlit run streamlit_app.py

Covers syllabus topics:
- Unit I: AI Applications — web-based AI system
- Unit VI: AI tools and visualization, data pipelines
"""

import os, sys
import streamlit as st
sys.path.insert(0, os.path.dirname(__file__))

from config import RedditConfig, DomainConfig
from memory import ConversationMemory
from reddit_client import RedditClient
from response_builder import ResponseBuilder

st.set_page_config(page_title="MindBot — Reddit Edition", page_icon="🧠", layout="centered")

st.markdown("""
<style>
.bot-msg   { background:#e8f4fd; border-radius:12px; padding:12px 16px; margin:8px 0; }
.user-msg  { background:#f0f9f0; border-radius:12px; padding:12px 16px; margin:8px 0; text-align:right; }
.reddit-tag{ background:#FF4500; color:white; border-radius:6px; padding:2px 8px; font-size:11px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "memory"   not in st.session_state: st.session_state.memory   = ConversationMemory(max_turns=10)
if "domain"   not in st.session_state: st.session_state.domain   = DomainConfig()
if "r_config" not in st.session_state: st.session_state.r_config = RedditConfig()
if "builder"  not in st.session_state: st.session_state.builder  = ResponseBuilder(st.session_state.domain)
if "messages" not in st.session_state: st.session_state.messages = []
if "reddit"   not in st.session_state:
    cid = os.getenv("REDDIT_CLIENT_ID")
    cs  = os.getenv("REDDIT_CLIENT_SECRET")
    if cid and cs:
        st.session_state.reddit = RedditClient(cid, cs, st.session_state.r_config.user_agent)
    else:
        st.session_state.reddit = None

# ── Helper ────────────────────────────────────────────────────────────────────
def get_response(user_msg: str) -> str:
    domain  = st.session_state.domain
    memory  = st.session_state.memory
    builder = st.session_state.builder
    rc      = st.session_state.r_config
    reddit  = st.session_state.reddit

    if any(kw in user_msg.lower() for kw in domain.crisis_keywords):
        return domain.crisis_response

    intent     = builder.detect_intent(user_msg)
    query      = builder.get_search_query(user_msg, intent)
    subreddits = builder.get_subreddits_for_intent(intent)

    posts = []
    if reddit and reddit.connected:
        try:
            posts = reddit.search_posts(query, subreddits, rc.max_posts, rc.min_upvotes, rc.time_filter)
        except Exception:
            pass

    if posts or (reddit and reddit.connected):
        reply = builder.build_response(user_msg, posts, intent)
    else:
        reply = builder.build_fallback_response()

    memory.add_turn(user_msg, reply)
    return reply

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("🔑 Reddit API Credentials")
    cid = st.text_input("Client ID",     type="password", placeholder="From reddit.com/prefs/apps")
    cs  = st.text_input("Client Secret", type="password", placeholder="Secret key")

    if st.button("Connect to Reddit"):
        if cid and cs:
            rc = st.session_state.r_config
            st.session_state.reddit = RedditClient(cid, cs, rc.user_agent)
            if st.session_state.reddit.connected:
                st.success("✅ Reddit API Connected!")
            else:
                st.error("❌ Connection failed. Check your credentials.")
        else:
            st.warning("Please enter both Client ID and Client Secret.")

    if st.session_state.reddit:
        status = "✅ Connected" if st.session_state.reddit.connected else "❌ Disconnected"
        st.caption(f"Reddit Status: {status}")

    st.divider()
    st.subheader("📊 Mood Tracker")
    mood_score = st.slider("Current Mood (1-10)", 1, 10, 5)
    mood_note  = st.text_input("What's contributing to this?", placeholder="Optional...")
    if st.button("Log Mood"):
        st.session_state.memory.log_mood(mood_score, mood_note)
        st.success(f"Mood {mood_score}/10 logged!")

    mood_log = st.session_state.memory.get_mood_trend()
    if mood_log:
        avg = st.session_state.memory.get_mood_average()
        st.caption(f"Session avg: **{avg}/10** over {len(mood_log)} entries")
        for entry in mood_log[-3:]:
            bar = "█" * entry["score"] + "░" * (10 - entry["score"])
            st.markdown(f"`{bar}` {entry['score']}/10")

    st.divider()
    st.subheader("🔍 Active Subreddits")
    for sub in st.session_state.r_config.subreddits:
        st.caption(f"• r/{sub}")

    st.divider()
    if st.button("🗑️ Reset Conversation"):
        st.session_state.memory.clear()
        st.session_state.messages.clear()
        st.rerun()

    st.divider()
    st.caption("🆘 **Crisis Helplines (India)**")
    st.caption("iCall: 9152987821")
    st.caption("Vandrevala: 1860-2662-345")
    st.caption("AASRA: 98204 66627")

# ── Main Chat Area ────────────────────────────────────────────────────────────
st.title("🧠 MindBot — Mental Health Support")
st.caption("Powered by Reddit Community | INT428 Project | Not a substitute for professional help")

if not st.session_state.reddit or not st.session_state.reddit.connected:
    st.warning("⚠️ Reddit API not connected. Enter credentials in the sidebar to enable community-powered responses.", icon="⚠️")

st.info("💙 I'm here to listen. I'm powered by real mental health community discussions, not an AI model. I am NOT a licensed therapist.", icon="ℹ️")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">🧑 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 <b>MindBot:</b> {msg["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("How are you feeling today?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Searching community posts..."):
        response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
