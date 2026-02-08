const DEFAULT_API_BASE = 'http://localhost:8000';

export function getApiBase() {
  return process.env.NEXT_PUBLIC_API_BASE || DEFAULT_API_BASE;
}

export async function postSearch(body: unknown) {
  const response = await fetch(`${getApiBase()}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Search request failed (${response.status})`);
  }

  return response;
}

export async function postLLMVerify(body: unknown) {
  const response = await fetch(`${getApiBase()}/api/llm/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`LLM verify failed (${response.status})`);
  }
  return response;
}
