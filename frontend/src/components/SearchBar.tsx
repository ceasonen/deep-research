'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import type { SearchMode } from '@/types';

interface SearchBarProps {
  loading: boolean;
  onSearch: (query: string, mode: SearchMode) => void;
  initialQuery?: string;
  initialMode?: SearchMode;
}

const modeTips: Record<SearchMode, string> = {
  quick: 'Fast web snapshot with concise synthesis.',
  deep: 'Broader retrieval and heavier evidence synthesis.',
  academic: 'General academic search behavior over web sources.',
  arxiv: 'Latest arXiv in cs.AI/cs.LG/cs.CL/cs.CV/stat.ML.',
};

const modePresets: Record<SearchMode, string[]> = {
  quick: ['OpenAI o1 update', 'MCP server best practices', 'AI agent evals'],
  deep: ['Long-context reasoning methods', 'Tool-use reliability metrics', 'RAG failure modes'],
  academic: ['Diffusion transformer survey', 'Multimodal benchmark leaderboards', 'Small language model training'],
  arxiv: ['multimodal reasoning', 'test-time scaling', 'agentic planning'],
};

const modeLabel: Record<SearchMode, string> = {
  quick: 'Quick',
  deep: 'Deep',
  academic: 'Academic',
  arxiv: 'ArXiv',
};

export function SearchBar({ loading, onSearch, initialQuery, initialMode }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<SearchMode>('quick');
  const presets = useMemo(() => modePresets[mode], [mode]);

  useEffect(() => {
    if (initialQuery) setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    if (initialMode) setMode(initialMode);
  }, [initialMode]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(query, mode);
  }

  return (
    <form id="search" onSubmit={submit} className="glass-panel section-enter stagger-1 space-y-4 p-4 md:p-5">
      <div className="flex flex-wrap gap-2">
        {(Object.keys(modeLabel) as SearchMode[]).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setMode(item)}
            className={`soft-ring rounded-full px-3 py-1 text-xs transition ${
              mode === item ? 'bg-ink text-white' : 'border border-ink/20 bg-white/70 text-ink'
            }`}
          >
            {modeLabel[item]}
          </button>
        ))}
      </div>

      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
        <label className="sr-only" htmlFor="query">
          Search Query
        </label>
        <input
          id="query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={
            mode === 'arxiv' ? 'Track latest papers in cs.AI / cs.LG / cs.CL / cs.CV / stat.ML...' : 'Ask anything with real-time sources...'
          }
          className="soft-ring h-12 rounded-2xl border border-ink/20 bg-white/85 px-4 text-sm text-ink outline-none transition focus:border-ember"
        />
        <div className="flex items-center rounded-2xl border border-ink/20 bg-white/70 px-3 text-xs text-ink/75">
          Mode: {modeLabel[mode]}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="soft-ring h-12 rounded-2xl bg-ink px-5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Searching...' : mode === 'arxiv' ? 'Scan Papers' : 'Search'}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-sand px-3 py-1 text-xs text-ink/75">{modeTips[mode]}</span>
        {presets.map((item) => (
          <button
            key={`${mode}-${item}`}
            type="button"
            onClick={() => {
              setQuery(item);
              onSearch(item, mode);
            }}
            className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/70 px-3 py-1 text-xs text-ink/85"
          >
            {item}
          </button>
        ))}
      </div>
    </form>
  );
}
