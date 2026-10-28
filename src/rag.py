"""
Phase 2 RAG: chunking, FAISS semantic search, and cited Q&A over loaded papers.
Retrieval is fully local; answers come from Groq (free tier) when GROQ_API_KEY
is set, otherwise an extractive answer built from the top passages.
"""
import functools
import importlib.util
import logging
import os

import numpy as np
import requests

logger = logging.getLogger(__name__)

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


# LITE mode: no torch/PEGASUS; ONNX embeddings (fastembed) + Groq summaries. Fits ~512MB-1GB hosts.
LITE = os.environ.get("LITE_MODE") == "1" or importlib.util.find_spec("sentence_transformers") is None


@functools.lru_cache(maxsize=1)
def _load_embedder():
    logger.info("Loading embedding model %s (lite=%s)", EMBED_MODEL, LITE)
    if LITE:
        from fastembed import TextEmbedding
        return TextEmbedding(EMBED_MODEL)
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL, device="cpu")


_CLEAN = str.maketrans({
    " ": " ", " ": " ", "‑": "-", "‐": "-",
    "【": "[", "】": "]",  # 【1】 -> [1]
})


def clean_text(text):
    """Normalize odd unicode (narrow spaces, non-breaking hyphens, 【】 citations)."""
    return text.translate(_CLEAN)


def paper_label(paper, idx):
    """Human-readable name for a paper dict (uploaded PDF or search result)."""
    return paper.get('filename') or paper.get('title') or f"Paper {idx}"


class PaperIndex:
    """FAISS index over chunks of the loaded papers."""

    def __init__(self, chunk_size=1000, chunk_overlap=150):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self._embedder = None
        self.index = None
        self.chunks = []  # [{'text', 'paper', 'year', 'source'}]

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = _load_embedder()
        return self._embedder

    def _embed(self, texts):
        if LITE:
            vecs = np.array(list(self.embedder.embed(texts)), dtype="float32")
            return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
        vecs = self.embedder.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(vecs, dtype="float32")

    def build(self, papers):
        """(Re)build the index from paper dicts with 'text' or 'abstract'."""
        import faiss
        self.chunks = []
        for i, paper in enumerate(papers, 1):
            body = paper.get('text') or paper.get('abstract')
            if not body:
                continue
            for piece in self.splitter.split_text(body):
                self.chunks.append({
                    'text': piece,
                    'paper': paper_label(paper, i),
                    'year': paper.get('year'),
                    'source': paper.get('source', 'upload'),
                })
        if not self.chunks:
            self.index = None
            return 0
        vecs = self._embed([c['text'] for c in self.chunks])
        self.index = faiss.IndexFlatIP(vecs.shape[1])  # cosine on normalized vecs
        self.index.add(vecs)
        return len(self.chunks)

    def search(self, query, k=5, paper=None, source=None, min_year=None, balanced=False):
        """Top-k chunks for query, optionally filtered by paper/source/year."""
        if self.index is None:
            return []
        qv = self._embed([query])
        # Over-fetch so post-filtering still leaves k results
        fetch = len(self.chunks) if (paper or source or min_year or balanced) else min(k, len(self.chunks))
        scores, ids = self.index.search(qv, fetch)
        hits = []
        for score, i in zip(scores[0], ids[0]):
            if i < 0:
                continue
            c = self.chunks[i]
            if paper and c['paper'] != paper:
                continue
            if source and c['source'] != source:
                continue
            if min_year and not _year_ok(c['year'], min_year):
                continue
            hits.append({**c, 'score': float(score)})
            if len(hits) == k and not balanced:
                break
        if balanced:
            hits = _balance(hits, k)
        return hits


def _balance(hits, k):
    """Best chunk from every paper first (so no paper is ignored), then fill by score."""
    seen, first = set(), []
    for h in hits:
        if h['paper'] not in seen:
            seen.add(h['paper'])
            first.append(h)
    picked = first[:k]
    for h in hits:
        if len(picked) >= k:
            break
        if h not in picked:
            picked.append(h)
    return sorted(picked, key=lambda h: -h['score'])


def _year_ok(year, min_year):
    try:
        return int(year) >= int(min_year)
    except (TypeError, ValueError):
        return False


def answer_question(question, hits, api_key=None):
    """Answer from retrieved chunks. Returns (answer, backend)."""
    if not hits:
        return "No relevant passages found in the loaded papers.", "none"
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            return _groq_answer(question, hits, api_key), f"groq:{GROQ_MODEL}"
        except Exception as e:
            logger.warning("Groq failed, using extractive fallback: %s", e)
    return _extractive_answer(hits), "extractive"


ANSWER_RULES = (
    "You are a precise research assistant. Answer using ONLY the numbered passages in the "
    "latest message, citing them inline like [1], [2]. Be specific and concrete: name the "
    "exact methods, models, datasets, metrics, numbers and findings the passages state, and "
    "say which paper each point comes from. Never give generic filler or restate the "
    "question. When several papers are involved, answer per paper (one bold paper name, then "
    "bullets). If the passages only partly answer, give what they support and say what is "
    "missing; if they do not contain the answer, say so plainly."
)


def _groq_answer(question, hits, api_key):
    context = "\n\n".join(
        f"[{n}] ({h['paper']})\n{h['text']}" for n, h in enumerate(hits, 1)
    )
    messages = [
        {"role": "system", "content": ANSWER_RULES},
        {"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"},
    ]
    resp = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.1},
        timeout=60,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return clean_text(resp.json()["choices"][0]["message"]["content"].strip())


def _extractive_answer(hits):
    top = hits[:2]
    return "\n\n".join(f"{h['text']} [{n}]" for n, h in enumerate(top, 1))


def stream_answer(question, hits, history=None, api_key=None):
    """Streaming variant of answer_question. Returns (token_iterator, backend).

    `history` is a list of prior {'role', 'content'} chat turns used for follow-ups.
    """
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            return _groq_stream(question, hits, history or [], api_key), f"groq:{GROQ_MODEL}"
        except Exception as e:
            logger.warning("Groq failed, using extractive fallback: %s", e)
    return iter([_extractive_answer(hits)]), "extractive"


def _groq_stream(question, hits, history, api_key):
    import json
    context = "\n\n".join(
        f"[{n}] ({h['paper']})\n{h['text']}" for n, h in enumerate(hits, 1)
    )
    messages = [{"role": "system", "content": ANSWER_RULES}]
    for turn in history[-6:]:
        messages.append({"role": turn["role"], "content": turn["content"][:1500]})
    messages.append({"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"})
    resp = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.1, "stream": True},
        timeout=60, stream=True,
    )
    resp.raise_for_status()  # raise before returning so the caller can fall back
    resp.encoding = "utf-8"  # SSE has no charset header; requests would guess latin-1 (mojibake)

    def tokens():
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            delta = json.loads(data)["choices"][0].get("delta", {})
            if delta.get("content"):
                yield clean_text(delta["content"])
    return tokens()
