"""FastAPI app entrypoint for AutoSearch AI."""

from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.models.schemas import HealthResponse, SearchRequest
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


def run_cli() -> None:
    parser = argparse.ArgumentParser(prog="autosearch", description="AutoSearch AI CLI")
    parser.add_argument("command", nargs="?", default="serve", choices=["serve"])
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", default=settings.port, type=int)
    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn

        uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=False)
