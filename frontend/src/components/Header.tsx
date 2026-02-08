import { ThemeToggle } from '@/components/ThemeToggle';

export function Header() {
  return (
    <header className="mx-auto flex w-full max-w-6xl flex-wrap items-start justify-between gap-4 px-4 py-8 md:py-10">
      <div className="section-enter">
        <p className="font-compact text-xs uppercase tracking-[0.32em] text-ink/60">AutoSearch Research Console</p>
        <h1 className="mt-2 font-display text-4xl text-ink md:text-6xl">ArXiv Radar + Live Evidence</h1>
        <p className="mt-3 max-w-2xl text-sm text-ink/70 md:text-base">
          A focused intelligence desk for fast AI paper triage: newest papers, direct PDF reading, and concise model-assisted analysis.
        </p>
      </div>
      <div className="section-enter stagger-1 flex items-center gap-2">
        <a href="#search" className="soft-ring hover-lift rounded-full border border-ink/20 bg-white/70 px-4 py-2 text-sm text-ink">
          Start
        </a>
        <ThemeToggle />
      </div>
    </header>
  );
}
