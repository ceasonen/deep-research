# AutoSearch AI

Open-source real-time AI search with source citations, plus an ArXiv-focused paper radar and built-in PDF reader.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-15-black.svg)](https://nextjs.org/)

## Highlights

- Search modes: `quick`, `deep`, `academic`, `arxiv`
- Multi-engine web aggregation: `duckduckgo`, `google`, `bing`, `brave`
- Async fetch + extraction pipeline with optional reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- SSE streaming answers and non-stream JSON responses
- Citation-aware markdown output with follow-up query suggestions
- ArXiv enrichment (`summary`, `method`, `limitations`, `repro difficulty`, `code link`) + `/reader` PDF page
- Runtime LLM override (OpenAI-compatible base URL/key/model per request)
- FastAPI backend + Next.js frontend + Docker Compose

## Project Structure

```text
backend/
  arxiv/       # arXiv client + paper analysis
  content/     # page fetch + text extraction
  llm/         # OpenAI-compatible client + synthesis
  pipeline/    # end-to-end orchestration + SSE events
  search/      # search engine adapters + aggregator
frontend/
  src/app/     # Next.js app routes (`/` and `/reader`)
tests/         # API and pipeline tests
docs/          # architecture, API reference, deployment, contributing
```

## Quick Start

### 1) Local development

```bash
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

Optional one-command startup on macOS:

```bash
./start_dev.command
```

### 2) Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

## Configuration

Use `.env` (see `.env.example`) to configure:

- LLM provider and defaults (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`)
- Auto key-file fallback (`LLM_API_KEY_FILE=key.txt`)
- Search engines and limits (`SEARCH_ENGINES`, `SEARCH_MAX_RESULTS`)
- ArXiv categories and fetch budget (`ARXIV_CATEGORIES`, `ARXIV_MAX_RESULTS`, `ARXIV_ANALYSIS_LLM_BUDGET`)
- Reranker, cache, and CORS behavior

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

### ArXiv mode

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"multimodal reasoning","mode":"arxiv","max_sources":8,"stream":false}'
```

### Verify runtime LLM config

```bash
curl -X POST http://localhost:8000/api/llm/verify \
  -H "Content-Type: application/json" \
  -d '{
    "base_url":"https://api.groq.com/openai/v1",
    "api_key":"YOUR_KEY",
    "model":"llama-3.3-70b-versatile"
  }'
```

### Runtime LLM override per search request

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query":"summarize latest test-time scaling papers",
    "mode":"arxiv",
    "stream":false,
    "llm_config":{
      "base_url":"https://api.groq.com/openai/v1",
      "api_key":"YOUR_KEY",
      "model":"llama-3.3-70b-versatile"
    }
  }'
```

## Development

Run backend tests:

```bash
pytest
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Docs

- `docs/architecture.md`
- `docs/api-reference.md`
- `docs/deployment.md`
- `docs/contributing.md`

## License

MIT - see `LICENSE`.
