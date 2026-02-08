'use client';

import { useMemo, useState } from 'react';

import { SourceCard } from '@/components/SourceCard';
import type { SearchSource } from '@/types';

interface SearchResultsProps {
  sources: SearchSource[];
}

export function SearchResults({ sources }: SearchResultsProps) {
  if (!sources.length) return null;
  const isArxiv = sources.some((source) => source.source_engine === 'arxiv' || Boolean(source.pdf_url));
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'relevance' | 'latest' | 'title'>('relevance');
  const [codeOnly, setCodeOnly] = useState(false);

  const filtered = useMemo(() => {
    let items = [...sources];
    if (isArxiv && codeOnly) {
      items = items.filter((source) => Boolean(source.code_repo_url));
    }

    items.sort((a, b) => {
      if (sortBy === 'title') {
        return a.title.localeCompare(b.title);
      }
      if (sortBy === 'latest') {
        const aTime = a.published_date ? Date.parse(a.published_date) : 0;
        const bTime = b.published_date ? Date.parse(b.published_date) : 0;
        return bTime - aTime;
      }
      return (b.relevance_score || 0) - (a.relevance_score || 0);
    });
    return items;
  }, [sources, isArxiv, sortBy, codeOnly]);

  return (
    <section className="section-enter stagger-3 space-y-3">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <h3 className="font-display text-2xl text-ink">{isArxiv ? 'Paper Feed' : 'Sources'}</h3>
        <p className="font-compact text-xs uppercase tracking-[0.22em] text-ink/60">{filtered.length} cards</p>
      </div>

      <div className="glass-panel flex flex-wrap items-center gap-2 p-3">
        <button
          type="button"
          onClick={() => setViewMode('grid')}
          className={`soft-ring rounded-full px-3 py-1 text-xs transition ${viewMode === 'grid' ? 'bg-ink text-white' : 'border border-ink/20 bg-white/70 text-ink'}`}
        >
          Grid
        </button>
        <button
          type="button"
          onClick={() => setViewMode('list')}
          className={`soft-ring rounded-full px-3 py-1 text-xs transition ${viewMode === 'list' ? 'bg-ink text-white' : 'border border-ink/20 bg-white/70 text-ink'}`}
        >
          List
        </button>
        <select
          value={sortBy}
          onChange={(event) => setSortBy(event.target.value as 'relevance' | 'latest' | 'title')}
          className="soft-ring ml-auto rounded-full border border-ink/20 bg-white/80 px-3 py-1 text-xs text-ink outline-none"
        >
          <option value="relevance">Sort: Relevance</option>
          <option value="latest">Sort: Latest</option>
          <option value="title">Sort: Title</option>
        </select>
        {isArxiv ? (
          <button
            type="button"
            onClick={() => setCodeOnly((prev) => !prev)}
            className={`soft-ring rounded-full px-3 py-1 text-xs transition ${codeOnly ? 'bg-mint/25 text-ink border border-mint/70' : 'border border-ink/20 bg-white/70 text-ink'}`}
          >
            Code Only
          </button>
        ) : null}
      </div>

      <div className={`grid gap-3 ${viewMode === 'grid' ? 'md:grid-cols-2' : 'grid-cols-1'}`}>
        {filtered.map((source, index) => (
          <SourceCard key={`${source.url}-${index}`} source={source} index={index} viewMode={viewMode} />
        ))}
      </div>
    </section>
  );
}
