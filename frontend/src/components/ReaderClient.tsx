'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function getSafeArxivPdfUrl(raw: string | undefined): string {
  if (!raw) return '';
  try {
    const parsed = new URL(raw);
    const isHttp = parsed.protocol === 'https:' || parsed.protocol === 'http:';
    const isArxiv = parsed.hostname === 'arxiv.org' || parsed.hostname.endsWith('.arxiv.org');
    const looksPdf = parsed.pathname.includes('/pdf/');
    if (isHttp && isArxiv && looksPdf) {
      return parsed.toString();
    }
    return '';
  } catch {
    return '';
  }
}

export function ReaderClient() {
  const router = useRouter();
  const params = useSearchParams();
  const [loaded, setLoaded] = useState(false);
  const [slowLoad, setSlowLoad] = useState(false);
  const pdfUrl = useMemo(() => getSafeArxivPdfUrl(params.get('pdf') || ''), [params]);
  const title = (params.get('title') || 'ArXiv Paper').trim();
  const arxivId = params.get('id') || '';
  const published = params.get('published') || '';
  const authors = (params.get('authors') || '')
    .split('|')
    .map((item) => item.trim())
    .filter(Boolean);
  const categories = (params.get('categories') || '')
    .split('|')
    .map((item) => item.trim())
    .filter(Boolean);
  const codeRepo = params.get('code') || '';
  const method = params.get('method') || '';
  const limits = params.get('limits') || '';

  function goBack() {
    if (window.history.length > 1) {
      router.back();
      return;
    }
    router.push('/');
  }

  useEffect(() => {
    setLoaded(false);
    setSlowLoad(false);
    if (!pdfUrl) return;

    const timer = window.setTimeout(() => setSlowLoad(true), 6000);
    return () => window.clearTimeout(timer);
  }, [pdfUrl]);

  return (
    <section className="section-enter w-full space-y-4">
      <section className="glass-panel mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="font-compact text-xs uppercase tracking-[0.3em] text-ink/70">Reader</p>
          <h1 className="font-display text-2xl text-ink">{title}</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={goBack}
            className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/70 px-4 py-2 text-sm text-ink"
          >
            Back
          </button>
          {pdfUrl ? (
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/70 px-4 py-2 text-sm text-ink"
            >
              Open in New Tab
            </a>
          ) : null}
        </div>
      </section>

      <section className="mx-auto grid w-full max-w-6xl gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
        <section className="glass-panel overflow-hidden p-2">
          {pdfUrl ? (
            <div className="relative h-[78vh] w-full overflow-hidden rounded-xl border border-ink/10 bg-white/70">
              {!loaded ? (
                <div className="absolute inset-0 z-10 flex items-center justify-center bg-sand/70">
                  <div className="text-center">
                    <div className="mx-auto h-2 w-44 overflow-hidden rounded-full bg-ink/10">
                      <div className="h-2 w-1/3 animate-[progress_1.1s_infinite] rounded-full bg-mint" />
                    </div>
                    <p className="mt-3 text-sm text-ink/70">Loading PDF viewer...</p>
                    {slowLoad ? (
                      <a
                        href={pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-3 inline-flex rounded-full border border-ink/20 bg-white/80 px-4 py-2 text-xs text-ink"
                      >
                        If embed is blocked, open PDF in new tab
                      </a>
                    ) : null}
                  </div>
                </div>
              ) : null}
              <iframe
                src={pdfUrl}
                title={title}
                className="h-full w-full"
                referrerPolicy="no-referrer"
                onLoad={() => setLoaded(true)}
              />
            </div>
          ) : (
            <div className="rounded-xl border border-ember/30 bg-ember/10 p-8 text-sm text-ink/80">
              <p className="font-semibold text-ember">Invalid PDF URL</p>
              <p className="mt-1">Please open a paper from the ArXiv feed to enter the reader.</p>
              <button
                type="button"
                onClick={() => router.push('/')}
                className="soft-ring mt-4 rounded-full border border-ink/20 bg-white/70 px-4 py-2 text-xs text-ink"
              >
                Return Home
              </button>
            </div>
          )}
        </section>

        <aside className="glass-panel h-fit space-y-3 p-4 lg:sticky lg:top-4">
          <p className="font-compact text-xs uppercase tracking-[0.24em] text-ink/60">Paper Sheet</p>
          {arxivId ? <p className="text-xs text-ink/80"><span className="font-semibold">ID:</span> {arxivId}</p> : null}
          {published ? (
            <p className="text-xs text-ink/80">
              <span className="font-semibold">Published:</span> {published.slice(0, 10)}
            </p>
          ) : null}
          {categories.length ? (
            <div className="flex flex-wrap gap-1.5">
              {categories.slice(0, 6).map((category) => (
                <span key={category} className="rounded-full border border-ink/15 bg-sand px-2 py-1 text-[10px] text-ink/80">
                  {category}
                </span>
              ))}
            </div>
          ) : null}
          {authors.length ? (
            <div>
              <p className="text-xs font-semibold text-ink/85">Authors</p>
              <p className="mt-1 text-xs text-ink/75">{authors.slice(0, 8).join(', ')}</p>
            </div>
          ) : null}
          {method ? (
            <div>
              <p className="text-xs font-semibold text-ink/85">Method Highlights</p>
              <p className="mt-1 text-xs text-ink/75">{method}</p>
            </div>
          ) : null}
          {limits ? (
            <div>
              <p className="text-xs font-semibold text-ink/85">Limitations</p>
              <p className="mt-1 text-xs text-ink/75">{limits}</p>
            </div>
          ) : null}
          {codeRepo ? (
            <a
              href={codeRepo}
              target="_blank"
              rel="noreferrer"
              className="soft-ring inline-flex rounded-full border border-ink/20 bg-white/75 px-3 py-1.5 text-xs text-ink"
            >
              Open Code Repository
            </a>
          ) : null}
        </aside>
      </section>
    </section>
  );
}
