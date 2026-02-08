'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { useSSE } from '@/hooks/useSSE';
import { postSearch } from '@/lib/api';
import type { RuntimeLLMConfig, SearchMode, SearchResponse, SearchSource } from '@/types';

interface SearchState {
  query: string;
  mode: SearchMode;
  answer: string;
  sources: SearchSource[];
  relatedQueries: string[];
  searchTime: number;
  modelUsed: string;
  loading: boolean;
  streaming: boolean;
  error: string | null;
}

const initialState: SearchState = {
  query: '',
  mode: 'quick',
  answer: '',
  sources: [],
  relatedQueries: [],
  searchTime: 0,
  modelUsed: '',
  loading: false,
  streaming: false,
  error: null,
};

const STORAGE_KEY = 'autosearch:last-state:v1';

export function useSearch() {
  const { streamSearch } = useSSE();
  const [state, setState] = useState<SearchState>(initialState);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setHydrated(true);
        return;
      }

      const parsed = JSON.parse(raw) as Partial<SearchState>;
      setState((prev) => ({
        ...prev,
        ...parsed,
        loading: false,
        streaming: false,
        error: null,
      }));
    } catch {
      // Ignore storage hydration errors and continue with defaults.
    } finally {
      setHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    try {
      const snapshot: SearchState = {
        ...state,
        loading: false,
        streaming: false,
        error: null,
      };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    } catch {
      // Ignore storage write failures.
    }
  }, [state, hydrated]);

  const runSearch = useCallback(
    async (query: string, mode: SearchMode = 'quick', streaming = true, llmConfig?: RuntimeLLMConfig) => {
      if (!query.trim()) return;

      setState((prev) => ({
        ...prev,
        query,
        mode,
        answer: '',
        sources: [],
        relatedQueries: [],
        loading: true,
        streaming,
        error: null,
      }));

      if (!streaming) {
        try {
          const response = await postSearch({
            query,
            mode,
            max_sources: 6,
            stream: false,
            llm_config: llmConfig,
          });
          const data = (await response.json()) as SearchResponse;
          setState((prev) => ({
            ...prev,
            answer: data.answer,
            sources: data.sources,
            relatedQueries: data.related_queries,
            searchTime: data.search_time,
            modelUsed: data.model_used,
            loading: false,
          }));
        } catch (error) {
          setState((prev) => ({ ...prev, loading: false, error: (error as Error).message }));
        }
        return;
      }

      await streamSearch(
        { query, mode, max_sources: 6, language: 'en', llm_config: llmConfig },
        {
          onEvent: (event, data) => {
            if (event === 'sources') {
              setState((prev) => ({ ...prev, sources: data.items || [] }));
              return;
            }
            if (event === 'answer_chunk') {
              setState((prev) => ({ ...prev, answer: `${prev.answer}${data.chunk || ''}` }));
              return;
            }
            if (event === 'answer_end') {
              setState((prev) => ({
                ...prev,
                answer: data.answer || prev.answer,
                sources: data.sources || prev.sources,
                relatedQueries: data.related_queries || [],
                searchTime: data.search_time || 0,
                modelUsed: data.model_used || '',
                loading: false,
                streaming: false,
              }));
              return;
            }
            if (event === 'error') {
              setState((prev) => ({
                ...prev,
                loading: false,
                streaming: false,
                error: data.message || 'Streaming failed',
              }));
            }
          },
          onDone: () => {
            setState((prev) => ({ ...prev, loading: false, streaming: false }));
          },
          onError: (error) => {
            setState((prev) => ({ ...prev, loading: false, streaming: false, error: error.message }));
          },
        },
      );
    },
    [streamSearch],
  );

  const reset = useCallback(() => {
    setState(initialState);
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore storage delete failures.
    }
  }, []);

  return useMemo(() => ({ ...state, runSearch, reset }), [state, runSearch, reset]);
}
