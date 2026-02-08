# API Reference

## `GET /api/health`
Returns service health and runtime capability info.

Response fields:
- `status`
- `version`
- `llm_connected`
- `reranker_loaded`
- `search_engines`

## `POST /api/search`
Search and synthesize answer.

Request body:
- `query` (string, required)
- `mode` (`quick | deep | academic`)
- `max_sources` (1-20)
- `language` (default `en`)
- `stream` (boolean)

When `stream=true`, response is `text/event-stream` with events:
- `sources`
- `answer_start`
- `answer_chunk`
- `answer_end`
- `error`
