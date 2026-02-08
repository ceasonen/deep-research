'use client';

import { FormEvent, useState } from 'react';

import type { SearchMode } from '@/types';

interface SearchBarProps {
  loading: boolean;
  onSearch: (query: string, mode: SearchMode) => void;
}

export function SearchBar({ loading, onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<SearchMode>('quick');

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(query, mode);
  }

  return (
    <form onSubmit={submit} className="rounded-3xl border border-ink/15 bg-white/70 p-4 shadow-soft backdrop-blur">
      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={mode === 'arxiv' ? 'Track latest papers in cs.AI/cs.LG/cs.CL/cs.CV/stat.ML...' : 'Ask anything with real-time sources...'}
          className="h-12 rounded-2xl border border-ink/20 bg-white px-4 text-sm text-ink outline-none ring-0 transition focus:border-ember"
        />
        <select
          value={mode}
          onChange={(event) => setMode(event.target.value as SearchMode)}
          className="h-12 rounded-2xl border border-ink/20 bg-white px-3 text-sm text-ink"
        >
          <option value="quick">Quick</option>
          <option value="deep">Deep</option>
          <option value="academic">Academic</option>
          <option value="arxiv">ArXiv Radar</option>
        </select>
        <button
          type="submit"
          disabled={loading}
          className="h-12 rounded-2xl bg-ink px-5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
}
