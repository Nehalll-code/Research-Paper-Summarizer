# Research Paper Summarizer

Advanced AI-powered research paper analysis platform with PEGASUS-ArXiv summarization.

## 🎯 Features

- 🔍 **Search Papers** - Find papers from arXiv & Semantic Scholar
- 📤 **Upload PDFs** - Extract text from local PDF files
- ✨ **AI Summarization** - PEGASUS-ArXiv powered summaries
- 🎨 **Beautiful UI** - Modern dark theme with Streamlit
- 📥 **Download Results** - Export summaries as text files

## 🚀 Quick Start

### Installation

## 💬 Ask Papers (RAG)

Phase 2 adds retrieval-augmented Q&A over your paper library:

- Build a library from search results and uploaded PDFs (sidebar)
- Papers are chunked, embedded locally (all-MiniLM-L6-v2) and indexed with FAISS
- Ask questions in a chat; answers cite numbered source passages
- Filter by paper, source and year, or use semantic search only
- Answers come from Groq (free tier); set `GROQ_API_KEY` in a `.env` file
  (see `.env.example`). Without a key you still get the top matching passages.

See [DEPLOY.md](DEPLOY.md) for deployment.
