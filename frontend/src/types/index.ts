export type SearchMode = 'quick' | 'deep' | 'academic' | 'arxiv';

export interface RuntimeLLMConfig {
  base_url?: string;
  api_key?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface SearchSource {
  title: string;
  url: string;
  snippet: string;
  content?: string;
  relevance_score?: number;
  source_engine?: string;
  published_date?: string;
  arxiv_id?: string;
  pdf_url?: string;
  authors?: string[];
  categories?: string[];
  ai_summary_3lines?: string;
  method_highlights?: string;
  limitations?: string;
  reproduction_difficulty?: string;
  code_repo_url?: string;
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
