import { SourceCard } from '@/components/SourceCard';
import type { SearchSource } from '@/types';

interface SearchResultsProps {
  sources: SearchSource[];
}

export function SearchResults({ sources }: SearchResultsProps) {
  if (!sources.length) return null;
  const isArxiv = sources.some((source) => source.source_engine === 'arxiv' || Boolean(source.pdf_url));

  return (
    <section className="space-y-3">
      <h3 className="font-display text-2xl text-ink">{isArxiv ? 'Paper Feed' : 'Sources'}</h3>
      <div className="grid gap-3 md:grid-cols-2">
        {sources.map((source, index) => (
          <SourceCard key={`${source.url}-${index}`} source={source} index={index} />
        ))}
      </div>
    </section>
  );
}
