<div align="center">

# 📚 Paper Chat

### Chat with your research papers — cited answers, semantic search, and summaries

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://nehalll-code-research-paper-summarizer-app-frqpfo.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![FAISS](https://img.shields.io/badge/Vector_Search-FAISS-0467DF?style=for-the-badge)](https://github.com/facebookresearch/faiss)

[Live demo](https://nehalll-code-research-paper-summarizer-app-frqpfo.streamlit.app/) • [Features](#-features) • [Setup](#-quick-start) • [Groq key](#-getting-and-adding-your-groq-api-key) • [How it works](#-how-it-works) • [Deploy](#-deployment) • [Roadmap](#-roadmap)

</div>

---

## 🎯 Overview

**Paper Chat** is a chat-style assistant for scientific literature. Build a library of papers by searching arXiv and Semantic Scholar, uploading PDFs, or pasting a PDF link. Then ask questions in plain English. Answers stream in word by word and cite the exact passages they came from, so you can verify every claim.

It started as a PEGASUS-based summarizer (Phase 1) and now includes a full retrieval-augmented generation (RAG) pipeline (Phase 2).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Chat with your papers** | Streaming answers with inline `[1]`, `[2]` citations and expandable source passages |
| **Follow-up questions** | The last few turns are sent along, so you can ask "what about its limitations?" |
| **Multi-source retrieval** | Search arXiv and Semantic Scholar, then add results to your library |
| **PDF upload and links** | Extract text from uploaded PDFs or a direct PDF URL |
| **Semantic search** | Papers are chunked, embedded and indexed with FAISS; every paper contributes its best passage so none is ignored |
| **Summaries** | One click to summarize the whole library (per paper plus a combined synthesis) |
| **Filters** | Limit questions to one paper or to papers from a given year; number of retrieved passages is adjustable |
| **Search-only mode** | See the top matching passages without generating an answer |
| **Download chat** | Export the conversation as text |
| **Works without a key** | No Groq key? You still get semantic search results (no written answers) |

---

## 🚀 Quick start

### Prerequisites

- Python 3.10 or newer
- A free [Groq API key](#-getting-and-adding-your-groq-api-key) for written answers and (in lite mode) summaries
- Full local build only: about 4 GB of free RAM

### Install

```bash
git clone https://github.com/Nehalll-code/Research-Paper-Summarizer
cd Research-Paper-Summarizer

python -m venv hf_venv
# Windows (PowerShell):  .\hf_venv\Scripts\Activate.ps1
# macOS / Linux:         source hf_venv/bin/activate
```

Pick one build:

| Build | Command | Summaries | Embeddings | RAM |
|-------|---------|-----------|------------|-----|
| **Full** (local) | `pip install -r requirements-full.txt` | PEGASUS-ArXiv, runs locally | sentence-transformers (torch) | 4 GB+ |
| **Lite** (hosted) | `pip install -r requirements.txt` | Groq | fastembed (ONNX) | about 0.5 – 1 GB |

Lite mode switches on automatically when `sentence-transformers` is not installed, or when you set `LITE_MODE=1`.

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501.

---

## 🔑 Getting and adding your Groq API key

Groq has a free tier, so you don't need a credit card. The key is used for written answers and, in lite mode, for summaries.

### 1. Get a key

1. Go to [console.groq.com](https://console.groq.com) and sign up or log in.
2. Open **API Keys** in the left menu.
3. Click **Create API Key**, give it a name, and copy it right away (it starts with `gsk_` and is only shown once).

### 2. Add it — choose where you run the app

**Running locally (recommended: a `.env` file)**

1. In the project folder, copy the template: `copy .env.example .env` (Windows) or `cp .env.example .env` (macOS / Linux).
2. Open `.env` and set:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
3. Restart Streamlit. The app loads `.env` automatically. It is git-ignored, so the key is never committed.

**Running locally (other options)**

- One terminal only (PowerShell): `$env:GROQ_API_KEY="gsk_your_key_here"`
- One terminal only (macOS / Linux): `export GROQ_API_KEY=gsk_your_key_here`
- Permanent on Windows: `setx GROQ_API_KEY "gsk_your_key_here"`, then open a new terminal.

**Streamlit Community Cloud**

1. Open your app's page and click **Manage app**, then the **⋮** menu, then **Settings**, then **Secrets**.
2. Add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   LITE_MODE = "1"
   ```
3. Click **Save**, then **Reboot app**.

**Render**

Dashboard, then your service, then **Environment**, then **Add Environment Variable**: `GROQ_API_KEY` = your key. Render redeploys automatically.

### 3. Check it works

The sidebar status should show **🟢 Groq connected** and the model name. Under each answer you will see a small label such as `groq:openai/gpt-oss-120b`. If it says `extractive` instead, no key was found, or the Groq call failed and the app fell back to showing passages.

### Notes

- **Never commit or share your key.** If it leaks, delete it in the Groq console and create a new one.
- To use a different Groq model, set `GROQ_MODEL` (for example in `.env`). The default is `openai/gpt-oss-120b`. Groq retires models from time to time; the list of available ones is in the Groq console.
- The free tier has rate limits. If you hit them, wait a bit and retry.

---

## 💻 Usage

1. Click **➕ Add papers** in the sidebar.
   - **Search**: enter keywords, tick the results you want, click *Add selected*.
   - **Upload PDFs**: choose one or more files, click *Add uploaded PDFs*.
   - **PDF link**: paste a direct PDF URL (for example `https://arxiv.org/pdf/1706.03762`).
2. Ask a question in the chat box, or click one of the suggestions.
3. Open **📎 sources** under an answer to read the passages it was based on.
4. Click **✨ Summarize my library** for summaries of every paper plus a combined one.
5. Use **⚙️ Settings** to limit questions to one paper, filter by year, change how many passages are retrieved, or switch to search-only.

---

## 🏗️ How it works

```
 PDFs / arXiv / Semantic Scholar
              │
              ▼
   text extraction (PyPDF2)
              │
              ▼
   chunking (LangChain RecursiveCharacterTextSplitter, 1000 chars, 150 overlap)
              │
              ▼
   embeddings (all-MiniLM-L6-v2; sentence-transformers or fastembed/ONNX)
              │
              ▼
   FAISS index (cosine similarity)         ◄── your question
              │                                  │
              ▼                                  ▼
   balanced retrieval: best chunk from every paper first, then fill by score
              │
              ▼
   Groq LLM, streamed, answers only from the retrieved passages, with citations
```

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit (chat UI, custom CSS in `src/theme.py`) |
| Retrieval | arXiv API, Semantic Scholar |
| Extraction | PyPDF2, requests |
| Chunking | LangChain text splitters |
| Embeddings | all-MiniLM-L6-v2 via sentence-transformers (full) or fastembed (lite) |
| Vector search | FAISS (`IndexFlatIP` on normalized vectors) |
| Answers | Groq (OpenAI-compatible API, streaming) |
| Summaries | PEGASUS-ArXiv locally (full) or Groq (lite) |

### Project structure

```
app.py                    Streamlit app (chat UI, library, add-papers panel)
src/
  rag.py                  Chunking, FAISS index, balanced search, Groq streaming
  groq_summarizer.py      Lite-mode summarizer (Groq)
  summarizer.py           PEGASUS-ArXiv summarizer (full build)
  paper_retrieval.py      arXiv + Semantic Scholar search
  pdf_extractor.py        PDF text extraction from URLs
  theme.py                Chat-style CSS
tests/test_rag.py         Retrieval, filters and fallback tests
requirements.txt          Lite dependencies (hosted)
requirements-full.txt     Full local dependencies (PEGASUS + torch)
render.yaml, Dockerfile   Deployment configs
DEPLOY.md                 Deployment notes
```

### Run the tests

```bash
pip install pytest
pytest tests/
```

---

## ☁️ Deployment

The app is deployed on Streamlit Community Cloud in lite mode. See [DEPLOY.md](DEPLOY.md) for the full steps, including Render and Docker. In short:

1. Push the repo to GitHub.
2. At [share.streamlit.io](https://share.streamlit.io), choose **Create app**, pick the repo, branch `main`, file `app.py`.
3. In **Advanced settings → Secrets** add `GROQ_API_KEY` and `LITE_MODE = "1"` (see [above](#-getting-and-adding-your-groq-api-key)).
4. Deploy. The first question is slow while the embedding model downloads.

Vercel is not suitable: Streamlit needs a long-running server with websockets.

---

## ⚠️ Limitations

- Only text in PDFs is read. Scanned documents without a text layer, figures, and tables are not understood.
- Papers found through search are indexed by abstract only; upload the PDF for full-text answers.
- Answers are limited to the retrieved passages. If the right passage is not retrieved, the answer can miss it. Raise *Passages per answer* in Settings for broader questions.
- The library lives in the browser session and is cleared on refresh.
- On the free hosted tier the app sleeps when idle, and the first request after waking up is slow.
- Generated answers can still contain mistakes. Check the cited sources.

---

## 🛣️ Roadmap

### Phase 1: Core platform ✅

- [x] Multi-source paper retrieval (arXiv, Semantic Scholar)
- [x] PDF extraction
- [x] PEGASUS-ArXiv summarization
- [x] Batch summaries with a combined summary

### Phase 2: RAG and chat ✅

- [x] LangChain text splitting
- [x] FAISS vector index and semantic search
- [x] Q&A over papers with source attribution
- [x] Filtering by paper and year
- [x] Chat-style UI with streaming answers
- [x] Hosted lite deployment

### Ideas

- [ ] Persist libraries between visits
- [ ] Link each source back to its arXiv page
- [ ] Re-ranking for sharper retrieval
- [ ] OCR for scanned PDFs

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes and push the branch
4. Open a pull request

---

## 📄 License

No license file has been added yet. Add one (for example MIT) before others reuse the code.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast, free-tier LLM inference
- [Google Research](https://github.com/google-research/pegasus) for PEGASUS
- [arXiv](https://arxiv.org/) and [Semantic Scholar](https://www.semanticscholar.org/) for open paper data
- [FAISS](https://github.com/facebookresearch/faiss), [LangChain](https://www.langchain.com/), [sentence-transformers](https://www.sbert.net/), [fastembed](https://github.com/qdrant/fastembed) and [Streamlit](https://streamlit.io/)
