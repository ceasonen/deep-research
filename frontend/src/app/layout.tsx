import type { Metadata } from 'next';

import './globals.css';

export const metadata: Metadata = {
  title: 'AutoSearch AI',
  description: 'Open-source real-time AI search engine with citations',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
