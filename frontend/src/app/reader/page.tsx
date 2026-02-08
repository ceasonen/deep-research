import { Suspense } from 'react';

import { ReaderClient } from '@/components/ReaderClient';

export default function ReaderPage() {
  return (
    <main className="min-h-screen bg-gradient-main p-4 text-ink md:p-6">
      <Suspense fallback={<p className="mx-auto w-full max-w-6xl py-8 text-sm text-ink/70">Loading reader...</p>}>
        <ReaderClient />
      </Suspense>
    </main>
  );
}
