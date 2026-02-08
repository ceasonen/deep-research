import { Suspense } from 'react';

import { ReaderClient } from '@/components/ReaderClient';

export default function ReaderPage() {
  return (
    <main className="app-shell route-fade min-h-screen bg-gradient-main p-4 text-ink md:p-6">
      <div className="ambient-grid" />
      <div className="ambient-glow left" />
      <div className="ambient-glow right" />
      <Suspense
        fallback={
          <p className="glass-panel mx-auto w-full max-w-6xl py-8 text-center text-sm text-ink/70">Loading reader...</p>
        }
      >
        <ReaderClient />
      </Suspense>
    </main>
  );
}
