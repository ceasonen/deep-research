export function LoadingAnimation() {
  return (
    <div className="rounded-2xl border border-ink/15 bg-white/70 p-5 shadow-soft">
      <div className="flex items-center gap-2 text-sm text-ink/75">
        <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-ember" />
        Searching the web and synthesizing sources...
      </div>
      <div className="mt-3 h-2 w-full overflow-hidden rounded bg-sand">
        <div className="h-2 w-1/3 animate-[progress_1.2s_infinite] rounded bg-mint" />
      </div>
    </div>
  );
}
