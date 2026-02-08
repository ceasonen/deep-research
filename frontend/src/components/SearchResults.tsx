import { SourceCard } from '@/components/SourceCard';
import type { SearchSource } from '@/types';

interface SearchResultsProps {
  sources: SearchSource[];
}

export function SearchResults({ sources }: SearchResultsProps) {
  if (!sources.length) return null;

  return (
    <section className="space-y-3">
      <h3 className="font-display text-2xl text-ink">Sources</h3>
      <div className="grid gap-3 md:grid-cols-2">
        {sources.map((source, index) => (
          <SourceCard key={`${source.url}-${index}`} source={source} index={index} />
        ))}
      </div>
    </section>
  );
}
