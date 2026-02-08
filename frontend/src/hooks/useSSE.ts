import { useCallback } from 'react';

import { getApiBase } from '@/lib/api';

interface StreamHandlers {
  onEvent: (event: string, data: any) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

export function useSSE() {
  const streamSearch = useCallback(async (payload: Record<string, unknown>, handlers: StreamHandlers) => {
    const response = await fetch(`${getApiBase()}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, stream: true }),
    });

    if (!response.ok || !response.body) {
      handlers.onError(new Error(`Streaming failed (${response.status})`));
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const block of parts) {
          const lines = block.split('\n');
          const eventLine = lines.find((line) => line.startsWith('event:'));
          const dataLine = lines.find((line) => line.startsWith('data:'));
          if (!eventLine || !dataLine) continue;

          const event = eventLine.replace('event:', '').trim();
          const rawData = dataLine.replace('data:', '').trim();

          let parsed: any = rawData;
          try {
            parsed = JSON.parse(rawData);
          } catch {
            parsed = rawData;
          }

          handlers.onEvent(event, parsed);
        }
      }
      handlers.onDone();
    } catch (error) {
      handlers.onError(error as Error);
    } finally {
      reader.releaseLock();
    }
  }, []);

  return { streamSearch };
}
