'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import type { RuntimeLLMConfig } from '@/types';

const STORAGE_KEY = 'autosearch:runtime-llm:v1';

export function useRuntimeLLMConfig() {
  const [config, setConfig] = useState<RuntimeLLMConfig | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setHydrated(true);
        return;
      }
      const parsed = JSON.parse(raw) as RuntimeLLMConfig;
      setConfig(parsed);
    } catch {
      setConfig(null);
    } finally {
      setHydrated(true);
    }
  }, []);

  const save = useCallback((next: RuntimeLLMConfig | null) => {
    setConfig(next);
    try {
      if (!next) {
        localStorage.removeItem(STORAGE_KEY);
        return;
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // Ignore storage failures.
    }
  }, []);

  const clear = useCallback(() => save(null), [save]);

  return useMemo(
    () => ({
      config,
      save,
      clear,
      hydrated,
      isConfigured: Boolean(config?.base_url && config?.model),
    }),
    [config, save, clear, hydrated],
  );
}
