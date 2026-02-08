import type { SearchSource } from '@/types';

const READER_STATE_PREFIX = 'autosearch:reader:v1:';
const READER_LAST_KEY = 'autosearch:reader:last:v1';

export interface ReaderPaperState {
  pdf: string;
  title: string;
  id: string;
  published: string;
  authors: string[];
  categories: string[];
  code: string;
  method: string;
  limits: string;
}

function getStorage(): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

function makeReaderId(source: SearchSource): string {
  const base = source.arxiv_id || source.title || 'paper';
  const cleaned = base.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const entropy = Math.random().toString(36).slice(2, 8);
  return `${cleaned || 'paper'}-${Date.now().toString(36)}-${entropy}`;
}

export function buildReaderState(source: SearchSource): ReaderPaperState {
  return {
    pdf: source.pdf_url || '',
    title: source.title || 'ArXiv Paper',
    id: source.arxiv_id || '',
    published: source.published_date || '',
    authors: source.authors || [],
    categories: source.categories || [],
    code: source.code_repo_url || '',
    method: source.method_highlights || '',
    limits: source.limitations || '',
  };
}

export function saveReaderState(source: SearchSource): string {
  const rid = makeReaderId(source);
  const storage = getStorage();
  if (!storage) return rid;

  try {
    const payload = JSON.stringify(buildReaderState(source));
    storage.setItem(`${READER_STATE_PREFIX}${rid}`, payload);
    storage.setItem(READER_LAST_KEY, rid);
  } catch {
    // Ignore storage write failures and continue with URL-only fallback.
  }

  return rid;
}

export function loadReaderState(rid: string | null): ReaderPaperState | null {
  const storage = getStorage();
  if (!storage) return null;

  const targetRid = rid || storage.getItem(READER_LAST_KEY);
  if (!targetRid) return null;

  try {
    const raw = storage.getItem(`${READER_STATE_PREFIX}${targetRid}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as ReaderPaperState;
    return parsed;
  } catch {
    return null;
  }
}
