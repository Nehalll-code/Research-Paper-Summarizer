"""Chat-style theme for the Streamlit app (injected as CSS)."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b0d12;
    --surface: #12151c;
    --surface-2: #181c26;
    --border: #232838;
    --text: #e6e8ee;
    --muted: #8b93a7;
    --accent: #7c83ff;
    --accent-2: #a78bfa;
}

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }

/* Chrome removal */
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

/* Centered chat column */
.block-container { max-width: 820px; padding-top: 2.2rem; padding-bottom: 8rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: #0e1016; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
.brand { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 1rem; }
.brand span { background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.side-label { color: var(--muted); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; margin: 1.1rem 0 0.4rem; }
.paper-row { font-size: 0.86rem; color: var(--text); padding: 0.35rem 0; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap; }
.status { font-size: 0.8rem; color: var(--muted); padding: 0.5rem 0.7rem; border: 1px solid var(--border);
    border-radius: 10px; background: var(--surface); }

/* Hero */
.hero { text-align: center; padding: 3.2rem 0 1.6rem; }
.hero h1 { font-size: 2.3rem; font-weight: 700; letter-spacing: -0.03em; margin: 0 0 0.6rem; }
.hero h1 span { background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { color: var(--muted); font-size: 1.02rem; margin: 0; }

/* Buttons */
.stButton > button {
    border-radius: 12px; border: 1px solid var(--border); background: var(--surface);
    color: var(--text); font-weight: 500; text-align: left; padding: 0.7rem 0.9rem;
    transition: border-color .15s, background .15s, transform .1s;
}
.stButton > button:hover { border-color: var(--accent); background: var(--surface-2); color: var(--text); }
.stButton > button:active { transform: scale(0.98); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)); border: none; color: #fff;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.1); }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent; border: 1px solid transparent; border-radius: 16px;
    padding: 0.9rem 1rem; margin-bottom: 0.4rem;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--surface-2); border-color: var(--border);
}
[data-testid="stChatMessage"] p { line-height: 1.65; }

/* Chat input */
[data-testid="stChatInput"] { border-radius: 26px; border: 1px solid var(--border); background: var(--surface); }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(124,131,255,.18); }
[data-testid="stBottom"] > div { background: linear-gradient(180deg, transparent, var(--bg) 40%); }

/* Source passages */
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 12px; background: var(--surface); }
.src { border-left: 3px solid var(--accent); padding: 0.4rem 0.8rem; margin: 0.5rem 0; background: var(--surface-2);
    border-radius: 0 8px 8px 0; font-size: 0.88rem; color: #c9cde0; }
.src b { color: var(--text); }
.src small { color: var(--muted); }
.meta { color: var(--muted); font-size: 0.75rem; margin-top: 0.3rem; }

/* Dialog */
[data-testid="stDialog"] > div { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; }

/* Inputs & scrollbar */
.stTextInput input, .stNumberInput input { border-radius: 10px; }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 8px; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
