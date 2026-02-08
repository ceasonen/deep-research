import { formatHost } from '@/lib/utils';
import type { SearchSource } from '@/types';

interface SourceCardProps {
  source: SearchSource;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      className="group rounded-2xl border border-ink/15 bg-white/70 p-4 shadow-soft transition hover:-translate-y-0.5"
    >
      <p className="font-mono text-xs text-ink/60">[{index + 1}] {formatHost(source.url)}</p>
      <h4 className="mt-2 line-clamp-2 text-sm font-semibold text-ink group-hover:text-ember">{source.title}</h4>
      <p className="mt-2 line-clamp-3 text-xs text-ink/70">{source.snippet}</p>
    </a>
  );
}
