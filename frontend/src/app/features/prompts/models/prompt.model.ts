export interface Prompt {
  id: string;
  title: string;
  content: string;
  complexity: number;
  is_active: boolean;
  view_count: number;
  tags: string[];
  created_at: string;
  updated_at: string;
  created_by: string | null;
}

export interface PromptListResponse {
  results: Prompt[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CreatePromptRequest {
  title: string;
  content: string;
  complexity: number;
  tags: string[];
}

export interface PromptFilters {
  search?: string;
  complexity?: number | null;
  tag?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export interface Tag {
  id: number;
  name: string;
}

export interface AnalyticsData {
  top_viewed: Prompt[];
  complexity_distribution: { complexity: number; count: number }[];
  redis_status: string;
}

export interface AuthResponse {
  token: string;
  username: string;
}

export const COMPLEXITY_LABELS: Record<number, string> = {
  1: 'Trivial', 2: 'Simple', 3: 'Easy', 4: 'Moderate',
  5: 'Average', 6: 'Involved', 7: 'Complex', 8: 'Hard',
  9: 'Expert', 10: 'Master',
};

export const COMPLEXITY_COLORS: Record<number, string> = {
  1: '#22c55e', 2: '#4ade80', 3: '#86efac', 4: '#fde047',
  5: '#fbbf24', 6: '#fb923c', 7: '#f97316', 8: '#ef4444',
  9: '#dc2626', 10: '#991b1b',
};
