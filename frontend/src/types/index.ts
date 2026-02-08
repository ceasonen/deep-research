export type SearchMode = 'quick' | 'deep' | 'academic';

export interface SearchSource {
  title: string;
  url: string;
  snippet: string;
  content?: string;
  relevance_score?: number;
  source_engine?: string;
}

export interface SearchResponse {
  query: string;
  answer: string;
  sources: SearchSource[];
  related_queries: string[];
  search_time: number;
  model_used: string;
}

export interface SearchEvent {
  event: string;
  data: any;
}
