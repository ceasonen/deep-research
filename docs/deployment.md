# Deployment

## Local source install
```bash
pip install -e ".[all]"
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Docker Compose
```bash
cp .env.example .env
docker compose up --build -d
```

## Use local Ollama
```bash
export LLM_PROVIDER=ollama
export LLM_BASE_URL=http://localhost:11434/v1
export LLM_MODEL=llama3.1
```
Then start backend normally.
