import type { Metadata } from 'next';
import { Fraunces, Space_Grotesk } from 'next/font/google';

import './globals.css';

const fraunces = Fraunces({ subsets: ['latin'], variable: '--font-display' });
const space = Space_Grotesk({ subsets: ['latin'], variable: '--font-body' });

export const metadata: Metadata = {
  title: 'AutoSearch AI',
  description: 'Open-source real-time AI search engine with citations',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${space.variable} antialiased`}>{children}</body>
    </html>
  );
}
