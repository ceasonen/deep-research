import { ThemeToggle } from '@/components/ThemeToggle';

export function Header() {
  return (
    <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-8">
      <div>
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-ink/70">AutoSearch AI</p>
        <h1 className="mt-2 font-display text-4xl text-ink md:text-5xl">ArXiv Radar + Evidence Search</h1>
      </div>
      <ThemeToggle />
    </header>
  );
}
