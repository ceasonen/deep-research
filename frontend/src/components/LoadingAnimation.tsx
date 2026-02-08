export function LoadingAnimation() {
  return (
    <div className="glass-panel section-enter stagger-2 p-5">
      <div className="flex items-center gap-2 text-sm text-ink/75">
        <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-ember" />
        Retrieving sources, ranking evidence, and drafting answer...
      </div>
      <div className="mt-3 h-2 w-full overflow-hidden rounded bg-sand">
        <div className="h-2 w-1/3 animate-[progress_1.2s_infinite] rounded bg-mint" />
      </div>
      <div className="mt-4 grid gap-2 md:grid-cols-3">
        <div className="h-16 animate-pulse rounded-xl bg-white/65" />
        <div className="h-16 animate-pulse rounded-xl bg-white/65" />
        <div className="h-16 animate-pulse rounded-xl bg-white/65" />
      </div>
    </div>
  );
}
