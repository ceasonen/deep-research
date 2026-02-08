'use client';

import { useCallback } from 'react';

import { ApiConfigPanel } from '@/components/ApiConfigPanel';
import { AnswerPanel } from '@/components/AnswerPanel';
import { Header } from '@/components/Header';
import { LoadingAnimation } from '@/components/LoadingAnimation';
import { SearchBar } from '@/components/SearchBar';
import { SearchResults } from '@/components/SearchResults';
import { useSearch } from '@/hooks/useSearch';
import { useRuntimeLLMConfig } from '@/hooks/useRuntimeLLMConfig';

export default function Page() {
  const { config: runtimeLLMConfig, save: saveRuntimeLLMConfig } = useRuntimeLLMConfig();
  const { answer, sources, loading, streaming, relatedQueries, runSearch, error, searchTime, modelUsed, mode, query } = useSearch();
  const hasResults = Boolean(answer || sources.length);
  const runSearchWithConfig = useCallback(
    (nextQuery: string, nextMode = mode) => runSearch(nextQuery, nextMode, true, runtimeLLMConfig || undefined),
    [mode, runSearch, runtimeLLMConfig],
  );

  return (
    <main className="app-shell route-fade min-h-screen bg-gradient-main pb-14 text-ink">
      <ApiConfigPanel config={runtimeLLMConfig} onSave={saveRuntimeLLMConfig} />
      <div className="ambient-grid" />
      <div className="ambient-glow left" />
      <div className="ambient-glow right" />
      <div className="bg-orb" />
      {loading || streaming ? (
        <div className="fixed inset-x-0 top-0 z-40 h-1 overflow-hidden bg-transparent">
          <div className="h-1 w-1/4 animate-[progress_0.95s_infinite] rounded-r bg-mint" />
        </div>
      ) : null}
      <Header />

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4">
        <SearchBar
          loading={loading}
          onSearch={runSearchWithConfig}
          initialMode={mode}
          initialQuery={query}
          runtimeModel={runtimeLLMConfig?.model}
        />
        {runtimeLLMConfig?.model ? (
          <div className="glass-panel section-enter p-3 text-xs text-ink/80">
            Active Runtime Model: <span className="font-semibold">{runtimeLLMConfig.model}</span>
            {runtimeLLMConfig.model !== 'gemini-2.5-flash' ? (
              <span className="ml-2 text-ember">Not `gemini-2.5-flash`</span>
            ) : null}
          </div>
        ) : null}
        {!hasResults && !loading ? (
          <section className="glass-panel section-enter stagger-2 p-5">
            <p className="font-compact text-xs uppercase tracking-[0.22em] text-ink/60">Ready</p>
            <h2 className="mt-2 font-display text-3xl text-ink">Search any topic or scan fresh ArXiv papers</h2>
            <p className="mt-2 max-w-3xl text-sm text-ink/75">
              Use ArXiv mode for paper radar, or quick/deep modes for real-time web evidence with citation-grounded synthesis.
            </p>
          </section>
        ) : null}
        {loading ? <LoadingAnimation /> : null}
        {error ? <p className="section-enter rounded-xl bg-ember/10 p-3 text-sm text-ember">{error}</p> : null}
        <AnswerPanel answer={answer} streaming={streaming} model={modelUsed} searchTime={searchTime} sources={sources} />
        <SearchResults sources={sources} />

        {relatedQueries.length ? (
          <div className="glass-panel section-enter p-4">
            <h3 className="font-display text-xl">Follow-up Queries</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {relatedQueries.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => runSearchWithConfig(item, mode)}
                  className="soft-ring hover-lift rounded-full border border-ink/20 bg-sand px-3 py-1 text-xs transition hover:border-ember"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      {hasResults ? (
        <div className="fixed bottom-5 right-5 z-30 flex flex-col gap-2">
          <button
            type="button"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/80 px-3 py-2 text-xs text-ink shadow-soft"
          >
            Top
          </button>
          <button
            type="button"
            onClick={() => runSearchWithConfig('latest multimodal reasoning papers', 'arxiv')}
            className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/80 px-3 py-2 text-xs text-ink shadow-soft"
          >
            Fresh ArXiv
          </button>
        </div>
      ) : null}
    </main>
  );
}
