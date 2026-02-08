'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import type { SearchSource } from '@/types';

interface AnswerPanelProps {
  answer: string;
  streaming: boolean;
  model: string;
  searchTime: number;
  sources: SearchSource[];
}

export function AnswerPanel({ answer, streaming, model, searchTime, sources }: AnswerPanelProps) {
  const safeAnswer = answer.replace(/\[(\d+)\]/g, (_, n) => {
    const idx = Number(n) - 1;
    if (idx >= 0 && idx < sources.length) {
      return `[${n}](${sources[idx].url})`;
    }
    return `[${n}]`;
  });

  if (!answer && !streaming) return null;

  return (
    <section className="rounded-3xl border border-ink/15 bg-white/75 p-6 shadow-soft">
      <div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-ink/70">
        <span className="rounded-full bg-sand px-3 py-1">Model: {model || 'fallback'}</span>
        <span className="rounded-full bg-sand px-3 py-1">Time: {searchTime.toFixed(2)}s</span>
        {streaming ? <span className="rounded-full bg-ember/20 px-3 py-1 text-ember">Streaming</span> : null}
      </div>
      <div className="prose prose-sm max-w-none prose-a:text-ember prose-headings:text-ink prose-p:text-ink/90">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{safeAnswer}</ReactMarkdown>
        {streaming ? <span className="inline-block h-5 w-1 animate-pulse rounded bg-ink/70" /> : null}
      </div>
    </section>
  );
}
