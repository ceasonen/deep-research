# Architecture

## High-level flow
1. Receive query from web UI or REST API.
2. Dispatch concurrent search requests to enabled engines.
3. De-duplicate and score URLs.
4. Fetch top pages and extract readable content.
5. Optionally rerank with a small cross-encoder model.
6. Build evidence-grounded prompt and synthesize response.
7. Return non-stream JSON or SSE event stream.

## Backend modules
- `backend/search`: search adapters + aggregator
- `backend/content`: fetch and extraction pipeline
- `backend/models`: request/response schemas + reranker
- `backend/llm`: LLM client, prompt builder, synthesizer
- `backend/pipeline`: orchestration and SSE event format

## Reliability strategy
- Fail-open behavior: if one engine fails, continue with others.
- If content extraction fails, keep snippet-only sources.
- If LLM fails, return fallback source summary.
