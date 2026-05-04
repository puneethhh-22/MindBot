# 🧠 MindBot — Mental Health Support Chatbot
### INT428 — Foundations & Applications of AI | Powered by Reddit API

---

## 📁 Project Structure

```
mental_health_bot/
│
├── main.py              → Entry point (run this to start CLI chatbot)
├── chatbot.py           → Core engine: Reddit search + response assembly
├── config.py            → RedditConfig (credentials, subreddits) + DomainConfig
├── reddit_client.py     → PRAW Reddit API wrapper (replaces OpenAI client)
├── response_builder.py  → Intent detection + response assembly (replaces prompt_engine)
├── memory.py            → Conversation memory + mood tracking (unchanged)
├── ui.py                → CLI interface with commands
├── streamlit_app.py     → Web UI with Reddit credential input
├── requirements.txt     → Python dependencies (praw)
└── README.md            → This file
```

---

## 🔧 Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create a Reddit App (FREE — takes 2 minutes)

1. Go to **https://www.reddit.com/prefs/apps**
2. Scroll down → click **"Create App"** (or "Create Another App")
3. Fill in:
   - **Name**: MindBot (any name)
   - **Type**: Select **"script"**
   - **Redirect URI**: `http://localhost:8080`
4. Click **"Create app"**
5. Copy:
   - **client_id** — shown under your app name (14-character string)
   - **client_secret** — labelled "secret"

### Step 3: Set Your Credentials

**Windows (Command Prompt):**
```bash
set REDDIT_CLIENT_ID=your_client_id_here
set REDDIT_CLIENT_SECRET=your_client_secret_here
```

**Mac/Linux:**
```bash
export REDDIT_CLIENT_ID=your_client_id_here
export REDDIT_CLIENT_SECRET=your_client_secret_here
```

### Step 4: Run the Chatbot

**CLI Mode:**
```bash
python main.py
```

**Web UI (Streamlit):**
```bash
streamlit run streamlit_app.py
```
*(Enter credentials in the sidebar when using web mode)*

---

## 💬 CLI Commands

| Command    | Description                          |
|------------|--------------------------------------|
| `/help`    | Show all available commands          |
| `/mood`    | Log your current mood (1-10)         |
| `/journal` | Get a journaling prompt              |
| `/reddit`  | Show active subreddits and API status|
| `/reset`   | Clear conversation history           |
| `/summary` | View session stats and mood trend    |
| `/quit`    | Exit the chatbot                     |

---

## 🔄 How It Works (vs Original OpenAI Version)

| Component        | Original (OpenAI)            | This Version (Reddit API)          |
|------------------|------------------------------|------------------------------------|
| API              | OpenAI GPT-3.5-turbo         | Reddit API via PRAW                |
| Cost             | Paid per token               | **Completely FREE**                |
| Response source  | LLM generation               | Real community posts + templates   |
| Hallucination    | Possible                     | None — real posts only             |
| Intent detection | LLM understanding            | Keyword-based NLP (rule-based)     |
| Prompt engine    | System prompt + few-shot     | Response templates + coping tips   |
| Crisis handling  | Same — keyword detection      | Same — keyword detection           |
| Mood tracking    | Same                         | Same                               |

---

## 🌐 Subreddits Used

| Subreddit         | Purpose                          |
|-------------------|----------------------------------|
| r/mentalhealth    | General mental health support    |
| r/anxiety         | Anxiety-specific discussions     |
| r/depression      | Depression support               |
| r/stress          | Stress and burnout               |
| r/sleep           | Sleep issues and insomnia        |
| r/mindfulness     | Mindfulness and meditation       |
| r/selfimprovement | Coping strategies and growth     |

---

## 🎓 Syllabus Coverage Map (INT428)

| Unit    | Topic                          | Implemented In              |
|---------|--------------------------------|-----------------------------|
| Unit I  | AI in Healthcare domain        | `config.py`, `chatbot.py`   |
| Unit I  | Responsible AI                 | Crisis detection in `chatbot.py` |
| Unit IV | NLP — intent detection         | `response_builder.py`       |
| Unit IV | Building chatbots              | Entire project              |
| Unit IV | Context window management      | `memory.py`                 |
| Unit V  | Response template engineering  | `response_builder.py`       |
| Unit V  | Ethics & Responsible AI        | Crisis detection, disclaimers |
| Unit VI | External API integration       | `reddit_client.py`          |
| Unit VI | Unstructured data handling     | Post cleaning in `reddit_client.py` |
| Unit VI | AI Tools & Frameworks          | Streamlit in `streamlit_app.py` |

---

## 🆘 Crisis Helplines (India)
- **iCall**: 9152987821
- **Vandrevala Foundation**: 1860-2662-345
- **AASRA**: 98204 66627
- **Emergency**: 112

---

## ⚠️ Disclaimer
MindBot is an educational AI project. Content is sourced from public Reddit communities.
It is NOT a substitute for professional mental health care.
