# Deploying

The app needs several GB of RAM (PEGASUS + embedding model), so use a host with at
least 4 GB. Streamlit Community Cloud's free tier (~1 GB) is too small.

## Hugging Face Spaces (free, 16 GB CPU)

1. Create a Space at huggingface.co/new-space, SDK = **Docker**.
2. Add this to the top of `README.md` in the Space repo:
   ```
   ---
   title: Research Paper Summarizer
   sdk: docker
   app_port: 7860
   ---
   ```
3. Space **Settings -> Variables and secrets -> New secret**: `GROQ_API_KEY` = your key.
   (Optional variable: `GROQ_MODEL`.)
4. Push the code:
   ```
   git remote add space https://huggingface.co/spaces/<user>/<space>
   git push space main
   ```
   Never push `.env`; it is git-ignored and in `.dockerignore`.
5. The first build takes several minutes. The first PEGASUS/embedding load downloads
   the models, so the first request is slow.

## Local container check

```
docker build -t paper-summarizer .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key paper-summarizer
```
