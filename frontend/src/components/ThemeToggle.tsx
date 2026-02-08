'use client';

import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const saved = localStorage.getItem('autosearch-theme') as 'light' | 'dark' | null;
    const initial = saved || 'light';
    setTheme(initial);
    document.documentElement.dataset.theme = initial;
  }, []);

  function toggleTheme() {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    localStorage.setItem('autosearch-theme', next);
    document.documentElement.dataset.theme = next;
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="rounded-full border border-ink/20 bg-white/70 px-4 py-2 text-sm font-medium text-ink shadow-soft transition hover:-translate-y-0.5"
    >
      {theme === 'light' ? 'Dark' : 'Light'}
    </button>
  );
}
