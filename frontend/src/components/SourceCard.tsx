'use client';

import { useRouter } from 'next/navigation';

import { saveReaderState } from '@/lib/readerState';
import { formatHost } from '@/lib/utils';
import type { SearchSource } from '@/types';

interface SourceCardProps {
  source: SearchSource;
  index: number;
  viewMode?: 'grid' | 'list';
}

export function SourceCard({ source, index, viewMode = 'grid' }: SourceCardProps) {
  const router = useRouter();
  const isArxiv = source.source_engine === 'arxiv' || Boolean(source.pdf_url) || Boolean(source.arxiv_id);
  const listLayout = viewMode === 'list';

  function openReader() {
    if (!source.pdf_url) return;
    const rid = saveReaderState(source);
    const params = new URLSearchParams({
      rid,
      pdf: source.pdf_url,
      title: source.title || 'ArXiv Paper',
      id: source.arxiv_id || '',
    });
    router.push(`/reader?${params.toString()}`);
  }

  if (isArxiv) {
    return (
      <article className={`glass-panel hover-lift p-4 ${listLayout ? 'md:flex md:items-start md:gap-4' : ''}`}>
        <div className={listLayout ? 'md:flex-1' : ''}>
          <p className="font-compact text-[11px] uppercase tracking-[0.2em] text-ink/60">
            [{index + 1}] arXiv {source.arxiv_id ? `· ${source.arxiv_id}` : ''}
          </p>
          <h4 className="mt-2 line-clamp-2 text-base font-semibold text-ink md:text-lg">{source.title}</h4>
          {source.authors?.length ? (
            <p className="mt-2 line-clamp-2 text-xs text-ink/70">Authors: {source.authors.join(', ')}</p>
          ) : null}
          {source.categories?.length ? (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {source.categories.slice(0, 5).map((category) => (
                <span
                  key={`${source.url}-${category}`}
                  className="rounded-full border border-ink/15 bg-sand px-2 py-1 text-[10px] text-ink/80"
                >
                  {category}
                </span>
              ))}
            </div>
          ) : null}
          <p className={`mt-3 text-xs text-ink/80 ${listLayout ? 'line-clamp-3' : 'line-clamp-4'}`}>{source.snippet}</p>
          {source.ai_summary_3lines ? (
            <div className="mt-3 rounded-xl border border-ink/10 bg-sand/60 p-3">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-ink/70">3-line summary</p>
              <p className="mt-1 whitespace-pre-line text-xs text-ink/80">{source.ai_summary_3lines}</p>
            </div>
          ) : null}
          <div className="mt-3 space-y-1 text-xs text-ink/80">
            {source.method_highlights ? (
              <p>
                <span className="font-semibold">Method:</span> {source.method_highlights}
              </p>
            ) : null}
            {source.limitations ? (
              <p>
                <span className="font-semibold">Limits:</span> {source.limitations}
              </p>
            ) : null}
            {source.reproduction_difficulty ? (
              <p>
                <span className="font-semibold">Repro:</span> {source.reproduction_difficulty}
              </p>
            ) : null}
            {source.published_date ? (
              <p>
                <span className="font-semibold">Published:</span> {source.published_date.slice(0, 10)}
              </p>
            ) : null}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {source.pdf_url ? (
              <button
                type="button"
                onClick={openReader}
                className="soft-ring rounded-full bg-ink px-3 py-1.5 text-xs font-semibold text-white transition hover:opacity-90"
              >
                Read PDF
              </button>
            ) : null}
            {source.pdf_url ? (
              <a
                href={source.pdf_url}
                target="_blank"
                rel="noreferrer"
                className="soft-ring rounded-full border border-ink/20 px-3 py-1.5 text-xs text-ink transition hover:border-ember"
              >
                Open PDF
              </a>
            ) : null}
            {source.code_repo_url ? (
              <a
                href={source.code_repo_url}
                target="_blank"
                rel="noreferrer"
                className="soft-ring rounded-full border border-ink/20 px-3 py-1.5 text-xs text-ink transition hover:border-ember"
              >
                Code
              </a>
            ) : null}
          </div>
        </div>
      </article>
    );
  }

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      className="glass-panel hover-lift group block p-4"
    >
      <p className="font-compact text-[11px] uppercase tracking-[0.2em] text-ink/60">
        [{index + 1}] {formatHost(source.url)}
      </p>
      <h4 className="mt-2 line-clamp-2 text-base font-semibold text-ink transition group-hover:text-ember">{source.title}</h4>
      <p className="mt-2 line-clamp-3 text-sm text-ink/74">{source.snippet}</p>
    </a>
  );
}
