import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import {
  Prompt, PromptListResponse, CreatePromptRequest,
  PromptFilters, Tag, AnalyticsData,
} from '../models/prompt.model';

@Injectable({ providedIn: 'root' })
export class PromptService {
  private readonly base = `${environment.apiUrl}/prompts`;

  constructor(private http: HttpClient) {}

  getPrompts(filters: PromptFilters = {}): Observable<PromptListResponse> {
    let params = new HttpParams();
    if (filters.search)     params = params.set('search', filters.search);
    if (filters.complexity) params = params.set('complexity', String(filters.complexity));
    if (filters.tag)        params = params.set('tag', filters.tag);
    if (filters.sort)       params = params.set('sort', filters.sort);
    if (filters.page)       params = params.set('page', String(filters.page));
    if (filters.page_size)  params = params.set('page_size', String(filters.page_size));
    return this.http.get<PromptListResponse>(`${this.base}/`, { params });
  }

  getPrompt(id: string): Observable<Prompt> {
    return this.http.get<Prompt>(`${this.base}/${id}/`);
  }

  createPrompt(data: CreatePromptRequest): Observable<Prompt> {
    return this.http.post<Prompt>(`${this.base}/`, data);
  }

  updatePrompt(id: string, data: Partial<CreatePromptRequest>): Observable<Prompt> {
    return this.http.put<Prompt>(`${this.base}/${id}/`, data);
  }

  deletePrompt(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.base}/${id}/`);
  }

  getTags(): Observable<{ results: Tag[]; total: number }> {
    return this.http.get<{ results: Tag[]; total: number }>(`${environment.apiUrl}/tags/`);
  }

  getAnalytics(): Observable<AnalyticsData> {
    return this.http.get<AnalyticsData>(`${environment.apiUrl}/analytics/`);
  }
}
