'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

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
  const params = useSearchParams();
  const pdfUrl = getSafeArxivPdfUrl(params.get('pdf') || '');
  const title = (params.get('title') || 'ArXiv Paper').trim();

  return (
    <>
      <section className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 rounded-2xl border border-ink/15 bg-white/80 p-4 shadow-soft">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-ink/70">Reader</p>
          <h1 className="font-display text-2xl text-ink">{title}</h1>
        </div>
        <Link href="/" className="rounded-full border border-ink/20 px-4 py-2 text-sm transition hover:border-ember">
          Back
        </Link>
      </section>

      <section className="mx-auto mt-4 w-full max-w-6xl overflow-hidden rounded-2xl border border-ink/15 bg-white/85 shadow-soft">
        {pdfUrl ? (
          <iframe
            src={pdfUrl}
            title={title}
            className="h-[78vh] w-full"
            referrerPolicy="no-referrer"
          />
        ) : (
          <p className="p-8 text-sm text-ink/70">Invalid PDF URL. Please open a paper from the ArXiv feed.</p>
        )}
      </section>
    </>
  );
}
