"""
Paper Chat - chat with your research papers (Streamlit).
Chat-first UI: library in the sidebar, streaming cited answers from Groq.
"""
import io
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")  # GROQ_API_KEY

from src.paper_retrieval import PaperRetriever
from src.pdf_extractor import extract_text_from_pdf_url
from src.rag import GROQ_MODEL, LITE, PaperIndex, paper_label, stream_answer
from src.theme import inject_css

st.set_page_config(
    page_title="Paper Chat",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)
inject_css()

SUMMARIZE_CMD = "✨ Summarize my library"
SUGGESTIONS = [
    ("🧭", "What problem does each paper address?"),
    ("🧪", "What methods and datasets are used?"),
    ("⚖️", "Compare the papers: key differences, similarities and strongest results."),
    ("🚧", "What are the main limitations?"),
]

for key, default in {
    "papers": [], "messages": [], "search_results": [],
    "rag_index": None, "rag_signature": None, "toast": None, "show_add": False,
}.items():
    st.session_state.setdefault(key, default)


# ---------- helpers ----------

@st.cache_resource(show_spinner=False)
def get_summarizer():
    if LITE:  # hosted build: Groq summaries, no torch
        from src.groq_summarizer import GroqSummarizer
        return GroqSummarizer()
    from src.summarizer import PaperSummarizer
    return PaperSummarizer()


def add_to_library(new_papers):
    """Append papers, skipping ones already present. Returns count added."""
    existing = {paper_label(p, 0) for p in st.session_state.papers}
    added = 0
    for p in new_papers:
        if paper_label(p, 0) not in existing:
            st.session_state.papers.append(p)
            existing.add(paper_label(p, 0))
            added += 1
    return added


def extract_pdf_bytes(data):
    import PyPDF2
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    text = " ".join(" ".join((page.extract_text() or "") for page in reader.pages).split())
    return text


def ensure_index():
    """Rebuild the FAISS index whenever the library changes."""
    signature = tuple(
        (paper_label(p, i), len(p.get('text') or p.get('abstract') or ''))
        for i, p in enumerate(st.session_state.papers, 1)
    )
    if st.session_state.rag_signature != signature:
        with st.spinner("Indexing your library (first run downloads the embedding model)..."):
            idx = PaperIndex()
            idx.build(st.session_state.papers)
        st.session_state.rag_index = idx
        st.session_state.rag_signature = signature
    return st.session_state.rag_index


def render_sources(hits):
    if not hits:
        return
    with st.expander(f"📎 {len(hits)} source{'s' if len(hits) != 1 else ''}"):
        for n, h in enumerate(hits, 1):
            snippet = h['text'] if len(h['text']) < 600 else h['text'][:600] + "…"
            st.markdown(
                f"<div class='src'><b>[{n}] {h['paper']}</b> "
                f"<small>· similarity {h['score']:.2f}</small><br>{snippet}</div>",
                unsafe_allow_html=True,
            )


def render_message(msg):
    with st.chat_message(msg["role"], avatar="🧑‍🔬" if msg["role"] == "user" else "📚"):
        st.markdown(msg["content"])
        if msg.get("backend"):
            st.markdown(f"<div class='meta'>{msg['backend']}</div>", unsafe_allow_html=True)
        render_sources(msg.get("hits"))


def summarize_library():
    """Run PEGASUS over the library; returns markdown."""
    texts = [p.get('text') or p.get('abstract') for p in st.session_state.papers]
    names = [paper_label(p, i) for i, p in enumerate(st.session_state.papers, 1)]
    keep = [(n, t) for n, t in zip(names, texts) if t]
    if not keep:
        return "There is no text to summarize in your library."
    with st.spinner("Preparing summarizer (the first run can be slow)..."):
        summarizer = get_summarizer()
    with st.spinner(f"Summarizing {len(keep)} paper(s)..."):
        if len(keep) == 1:
            return f"**{keep[0][0]}**\n\n{summarizer.summarize(keep[0][1], max_length=300, min_length=150)}"
        summaries, meta = summarizer.summarize_multiple([t for _, t in keep])
    parts = [f"**{n}**\n\n{s}" for (n, _), s in zip(keep, summaries)]
    return "\n\n---\n\n".join(parts) + f"\n\n---\n\n### 🎯 Across all papers\n\n{meta}"


# ---------- add-papers dialog ----------

def add_papers_panel():
    """Inline panel (not st.dialog, which is fragile with uploads in Streamlit 1.38)."""
    head, close = st.columns([6, 1])
    head.markdown("#### ➕ Add papers")
    if close.button("✕", key="close_add", help="Close"):
        st.session_state.show_add = False
        st.rerun()
    t_search, t_upload, t_url = st.tabs(["🔍 Search", "📤 Upload PDFs", "🔗 PDF link"])

    with t_search:
        with st.form("search_form"):
            c1, c2 = st.columns([4, 1])
            query = c1.text_input("Search arXiv & Semantic Scholar",
                                  placeholder="e.g. attention mechanisms in transformers")
            n = c2.number_input("Results", 1, 10, 5)
            go = st.form_submit_button("Search", type="primary")
        if go and query:
            with st.spinner("Searching..."):
                try:
                    st.session_state.search_results = PaperRetriever().search(query, max_results=int(n))
                except Exception as e:
                    st.error(f"Search failed: {e}")
        chosen = []
        for i, paper in enumerate(st.session_state.search_results, 1):
            title = paper.get('title', f'Paper {i}')
            authors = paper.get('authors', '')
            if isinstance(authors, list):
                authors = ', '.join(authors[:3])
            ck, body = st.columns([1, 14])
            if ck.checkbox("add", key=f"pick_{i}_{title[:24]}", label_visibility="collapsed"):
                chosen.append(paper)
            with body:
                st.markdown(f"**{title}**  \n<span class='meta'>{authors} · {paper.get('year', '')} · "
                            f"{paper.get('source', '')}</span>", unsafe_allow_html=True)
                with st.expander("Abstract"):
                    st.write(paper.get('abstract', ''))
        if st.session_state.search_results:
            b1, b2 = st.columns(2)
            if b1.button(f"Add {len(chosen)} selected", type="primary", disabled=not chosen,
                         use_container_width=True):
                st.session_state.toast = f"Added {add_to_library(chosen)} paper(s)"
                st.session_state.show_add = False
                st.rerun()
            if b2.button("Add all results", use_container_width=True):
                st.session_state.toast = f"Added {add_to_library(st.session_state.search_results)} paper(s)"
                st.session_state.show_add = False
                st.rerun()

    with t_upload:
        files = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True)
        if st.button("Add uploaded PDFs", type="primary", disabled=not files):
            new = []
            for f in files:
                try:
                    text = extract_pdf_bytes(f.getvalue())
                    if len(text) > 100:
                        new.append({'filename': f.name, 'text': text, 'source': 'upload'})
                    else:
                        st.warning(f"Not enough text in {f.name}")
                except Exception as e:
                    st.error(f"{f.name}: {e}")
            if new:
                st.session_state.toast = f"Added {add_to_library(new)} paper(s)"
                st.session_state.show_add = False
                st.rerun()

    with t_url:
        url = st.text_input("Direct PDF URL", placeholder="https://arxiv.org/pdf/1706.03762")
        if st.button("Fetch & add", type="primary", disabled=not url):
            with st.spinner("Downloading..."):
                try:
                    text = extract_text_from_pdf_url(url)
                    if text and len(text) > 100:
                        add_to_library([{'filename': url.rstrip('/').split('/')[-1] or url,
                                         'text': text, 'source': 'upload'}])
                        st.session_state.toast = "Added paper from link"
                        st.session_state.show_add = False
                        st.rerun()
                    else:
                        st.warning("Couldn't extract enough text from that link.")
                except Exception as e:
                    st.error(f"Failed: {e}")


# ---------- sidebar ----------

with st.sidebar:
    st.markdown("<div class='brand'>📚 <span>Paper Chat</span></div>", unsafe_allow_html=True)
    if st.button("➕  Add papers", type="primary", use_container_width=True):
        st.session_state.show_add = True
        st.rerun()
    if st.button("💬  New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<div class='side-label'>Library</div>", unsafe_allow_html=True)
    if not st.session_state.papers:
        st.caption("No papers yet.")
    for i, p in enumerate(list(st.session_state.papers)):
        c1, c2 = st.columns([6, 1])
        c1.markdown(f"<div class='paper-row'>📄 {paper_label(p, i + 1)}</div>", unsafe_allow_html=True)
        if c2.button("✕", key=f"rm_{i}", help="Remove"):
            st.session_state.papers.pop(i)
            st.rerun()

    names = [paper_label(p, i) for i, p in enumerate(st.session_state.papers, 1)]
    with st.expander("⚙️ Settings"):
        paper_filter = st.selectbox("Limit to paper", ["All"] + names)
        min_year = st.number_input("From year", 0, 2100, 0)
        top_k = st.slider("Passages per answer", 1, 12, 8)
        search_only = st.toggle("Search only (no generated answer)")

    if st.session_state.messages:
        transcript = "\n\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages)
        st.download_button("📥 Download chat", transcript, "paper_chat.txt", use_container_width=True)

    st.markdown("<div class='side-label'>Status</div>", unsafe_allow_html=True)
    if LITE:
        st.caption("Lite mode: Groq summaries, ONNX embeddings")
    if os.environ.get("GROQ_API_KEY"):
        st.markdown(f"<div class='status'>🟢 Groq connected<br>{GROQ_MODEL}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status'>⚪ Offline mode<br>Set GROQ_API_KEY for AI answers</div>",
                    unsafe_allow_html=True)

if st.session_state.toast:
    st.toast(st.session_state.toast, icon="✅")
    st.session_state.toast = None


# ---------- main chat ----------

queued = st.session_state.pop("queued", None)

if st.session_state.show_add:
    with st.container(border=True):
        add_papers_panel()

if not st.session_state.messages and not queued and not st.session_state.show_add:
    st.markdown(
        "<div class='hero'><h1>Chat with your <span>research papers</span></h1>"
        "<p>Add papers, then ask questions. Answers cite the exact passages they came from.</p></div>",
        unsafe_allow_html=True,
    )
    if not st.session_state.papers:
        _, mid, _ = st.columns([1, 2, 1])
        if mid.button("➕  Add your first papers", type="primary", use_container_width=True, key="cta_add"):
            st.session_state.show_add = True
            st.rerun()
    else:
        cols = st.columns(2)
        for n, (icon, text) in enumerate(SUGGESTIONS):
            if cols[n % 2].button(f"{icon}  {text}", key=f"sugg_{n}", use_container_width=True):
                st.session_state.queued = text
                st.rerun()
        if st.button(SUMMARIZE_CMD, key="sugg_sum", use_container_width=True):
            st.session_state.queued = SUMMARIZE_CMD
            st.rerun()

for msg in st.session_state.messages:
    render_message(msg)

has_papers = bool(st.session_state.papers)
prompt = st.chat_input(
    "Ask about your papers..." if has_papers else "Add papers first to start chatting",
    disabled=not has_papers,
) or queued

if prompt:
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🔬"):
        st.markdown(prompt)

    reply = {"role": "assistant", "content": "", "backend": None, "hits": []}
    with st.chat_message("assistant", avatar="📚"):
        try:
            if prompt == SUMMARIZE_CMD:
                reply["content"] = summarize_library()
                reply["backend"] = f"groq:{GROQ_MODEL}" if LITE else "pegasus-arxiv"
                st.markdown(reply["content"])
            else:
                idx = ensure_index()
                hits = idx.search(
                    prompt, k=top_k, balanced=True,
                    paper=None if paper_filter == "All" else paper_filter,
                    min_year=int(min_year) or None,
                )
                reply["hits"] = hits
                if not hits:
                    reply["content"] = "I couldn't find anything relevant in your papers. " \
                                       "Try rephrasing, or check the filters in Settings."
                    st.markdown(reply["content"])
                elif search_only:
                    reply["content"] = "Here are the most relevant passages:"
                    reply["backend"] = "semantic search"
                    st.markdown(reply["content"])
                else:
                    tokens, backend = stream_answer(prompt, hits, history)
                    reply["content"] = st.write_stream(tokens)
                    reply["backend"] = backend
                    st.markdown(f"<div class='meta'>{backend}</div>", unsafe_allow_html=True)
                render_sources(hits)
        except Exception as e:
            reply["content"] = f"Something went wrong: {e}"
            st.error(reply["content"])
    st.session_state.messages.append(reply)
