"""
Lightweight summarizer that uses Groq instead of a local PEGASUS model.
Same interface as PaperSummarizer, so the app can swap it in (LITE mode).
"""
import logging
import os
import time

import requests

from src.rag import GROQ_MODEL, GROQ_URL, clean_text

logger = logging.getLogger(__name__)

MAX_INPUT_CHARS = 9000  # keeps requests inside Groq free-tier token limits


class GroqSummarizer:
    """Summarizes research papers with a hosted LLM."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to .env or the host's secrets.")

    def _chat(self, prompt):
        for attempt in range(2):
            resp = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": GROQ_MODEL, "temperature": 0.2,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=90,
            )
            if resp.status_code == 429 and attempt == 0:  # rate limited: wait once and retry
                time.sleep(5)
                continue
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return clean_text(resp.json()["choices"][0]["message"]["content"].strip())

    def summarize(self, text, max_length=300, min_length=150):
        if not text or len(text.strip()) < 100:
            return "Text too short to summarize."
        text = text[:MAX_INPUT_CHARS]
        return self._chat(
            f"Summarize this research paper in {min_length}-{max_length} words. Cover the problem, "
            "the method, the key quantitative results and the limitations. Be specific (name "
            "models, datasets, numbers). Plain prose, no preamble.\n\n" + text
        )

    def summarize_multiple(self, texts):
        summaries = [self.summarize(t) for t in texts]
        joined = "\n\n".join(f"Paper {i}: {s}" for i, s in enumerate(summaries, 1))
        meta = self._chat(
            "Write a 120-180 word synthesis of these paper summaries: shared themes, key "
            "differences, and how the findings relate. Be specific; no preamble.\n\n" + joined
        )
        return summaries, meta
