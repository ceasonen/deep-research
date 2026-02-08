"""FastAPI app entrypoint for AutoSearch AI."""

from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.models.schemas import HealthResponse, RuntimeLLMConfig, SearchRequest
from backend.pipeline.search_pipeline import SearchPipeline
from backend.utils.logger import setup_logging

settings = get_settings()
setup_logging(debug=settings.debug)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = SearchPipeline()


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        llm_connected=pipeline.synthesizer.client.is_available,
        reranker_loaded=pipeline.reranker.is_loaded,
        search_engines=[engine.name for engine in pipeline.aggregator.engines],
    )


@app.post("/api/search")
async def search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if request.stream:
        generator = pipeline.search_stream(request)
        return StreamingResponse(generator, media_type="text/event-stream")

    data = await pipeline.search_sync(request)
    return JSONResponse(content=data)


@app.post("/api/llm/verify")
async def verify_llm(config: RuntimeLLMConfig | None = None):
    runtime_cfg = config.model_dump(exclude_none=True) if config else None
    client = pipeline.synthesizer.client
    model_used = client.resolved_model(runtime_cfg)

    if not client.is_available_for(runtime_cfg):
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "model_used": model_used,
                "message": "LLM configuration is incomplete or unavailable.",
            },
        )

    result = await client.complete(
        system_prompt="You are a test endpoint. Reply in one short line.",
        user_prompt="Respond with: LLM_OK",
        runtime_config=runtime_cfg,
    )
    ok = bool(result.strip())
    message = result[:180] if ok else (client.last_error_message or "LLM request failed.")

    return {
        "ok": ok,
        "model_used": model_used,
        "message": message,
    }


frontend_export = Path("frontend/out")
if frontend_export.exists():
    app.mount("/_next", StaticFiles(directory=str(frontend_export / "_next")), name="next-static")


@app.get("/")
async def root():
    index = frontend_export / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "Backend is running. Start frontend at http://localhost:3000",
    }


@app.get("/{asset_path:path}")
async def frontend_asset(asset_path: str):
    if not frontend_export.exists():
        raise HTTPException(status_code=404, detail="Frontend export not found")

    cleaned = asset_path.strip("/")
    if not cleaned:
        index = frontend_export / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="index.html not found")

    target = frontend_export / cleaned
    if target.is_file():
        return FileResponse(target)

    html_target = frontend_export / f"{cleaned}.html"
    if html_target.is_file():
        return FileResponse(html_target)

    not_found = frontend_export / "404.html"
    if not_found.is_file():
        return FileResponse(not_found, status_code=404)
    raise HTTPException(status_code=404, detail="Not found")


def run_cli() -> None:
    parser = argparse.ArgumentParser(prog="autosearch", description="AutoSearch AI CLI")
    parser.add_argument("command", nargs="?", default="serve", choices=["serve"])
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", default=settings.port, type=int)
    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn

        uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=False)
