export function formatHost(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

export function relativeMs(seconds: number): string {
  return `${seconds.toFixed(2)}s`;
}
