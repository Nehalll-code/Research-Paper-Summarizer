# Deploying

Two builds share one codebase:

| | Full (local) | Lite (hosted) |
|---|---|---|
| Summaries | local PEGASUS-ArXiv | Groq |
| Embeddings | sentence-transformers (torch) | fastembed (ONNX) |
| Install | `requirements-full.txt` | `requirements.txt` |
| RAM | 4 GB+ | ~512 MB - 1 GB |

Lite mode turns on when `LITE_MODE=1` is set, or when `sentence-transformers`
is not installed. Answers always come from Groq, so every host needs `GROQ_API_KEY`.

## Streamlit Community Cloud (free, ~1 GB, recommended)

1. Push this repo to GitHub (`.env` is git-ignored; never commit keys).
2. share.streamlit.io -> **Create app** -> pick the repo, branch `main`, file `app.py`.
3. **Advanced settings -> Secrets**, add:
   ```
   GROQ_API_KEY = "your_key"
   LITE_MODE = "1"
   ```
4. Deploy. The first question is slow while the embedding model downloads.

## Render (free, 512 MB, sleeps when idle)

1. Push to GitHub, then Render -> **New -> Blueprint** and pick the repo
   (it reads `render.yaml`).
2. Set the `GROQ_API_KEY` env var when prompted.
3. If the service runs out of memory, use Streamlit Cloud instead.

Vercel is not suitable: it only runs short serverless functions, and Streamlit
needs a long-running server with websockets.

## Full build in a container (needs 4 GB+ RAM)

```
docker build -t paper-chat .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key paper-chat
```
Hugging Face Docker Spaces now require a PRO subscription for this.
