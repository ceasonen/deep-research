'use client';

import { AnswerPanel } from '@/components/AnswerPanel';
import { Header } from '@/components/Header';
import { LoadingAnimation } from '@/components/LoadingAnimation';
import { SearchBar } from '@/components/SearchBar';
import { SearchResults } from '@/components/SearchResults';
import { useSearch } from '@/hooks/useSearch';

export default function Page() {
  const { answer, sources, loading, streaming, relatedQueries, runSearch, error, searchTime, modelUsed } = useSearch();

  return (
    <main className="min-h-screen bg-gradient-main pb-14 text-ink">
      <div className="bg-orb" />
      <Header />

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4">
        <SearchBar loading={loading} onSearch={runSearch} />
        {loading ? <LoadingAnimation /> : null}
        {error ? <p className="rounded-xl bg-ember/10 p-3 text-sm text-ember">{error}</p> : null}
        <AnswerPanel answer={answer} streaming={streaming} model={modelUsed} searchTime={searchTime} sources={sources} />
        <SearchResults sources={sources} />

        {relatedQueries.length ? (
          <div className="rounded-2xl border border-ink/15 bg-white/70 p-4 shadow-soft">
            <h3 className="font-display text-xl">Related Queries</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {relatedQueries.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => runSearch(item, 'quick')}
                  className="rounded-full border border-ink/20 bg-sand px-3 py-1 text-xs transition hover:border-ember"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
