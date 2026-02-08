<div align="center">

# AutoSearch AI

### Your Open-Source Real-Time AI Search Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)

Search the live web, extract useful content, and generate evidence-backed answers with citations.

</div>

## Why this project
- Replaces paid/closed AI search tools with a self-hosted stack.
- Runs with free search by default (`DuckDuckGo`), optional premium engines.
- Supports both cloud LLM APIs and local OpenAI-compatible providers (e.g., Ollama).
- Designed for quick deploy, clear architecture, and contributor friendliness.

## Features
- Multi-engine search aggregation (`duckduckgo`, `google`, `bing`, `brave`)
- Async content fetch + robust text extraction
- Optional light reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Streaming answer generation through SSE
- Citation-aware markdown answers (`[1]`, `[2]`, ...)
- FastAPI backend + Next.js frontend + Docker support

## Quick Start

### 1) Local development
```bash
git clone https://github.com/yourusername/autosearch-ai.git
cd autosearch-ai
cp .env.example .env
pip install -e ".[all]"
uvicorn backend.main:app --reload --port 8000
```

In another terminal:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### 2) Docker
```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

## API

### Health
```bash
curl http://localhost:8000/api/health
```

### Search (streaming)
```bash
curl -N -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"latest open-source AI search tools","mode":"quick","stream":true}'
```

### Search (non-streaming)
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"what is retrieval augmented generation","mode":"deep","stream":false}'
```

## Architecture

```text
Query -> Multi-engine Search -> Content Fetch/Extract -> (Optional) Rerank -> LLM Synthesis -> Cited Answer
```

See docs:
- `docs/architecture.md`
- `docs/api-reference.md`
- `docs/deployment.md`
- `docs/contributing.md`

## Roadmap
- [x] Core search + answer pipeline
- [x] Streaming SSE API
- [x] Next.js frontend
- [x] Docker deployment
- [ ] Session memory and follow-up questions
- [ ] Knowledge graph visualization
- [ ] Browser extension
- [ ] Team workspaces and auth

## Contributing
PRs and issues are welcome. Please read `docs/contributing.md` first.

## License
MIT - see `LICENSE`.
