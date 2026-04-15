import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PromptService } from '../features/prompts/services/prompt.service';
import { AnalyticsData, COMPLEXITY_LABELS } from '../features/prompts/models/prompt.model';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './analytics.component.html',
  styleUrls: ['./analytics.component.scss'],
})
export class AnalyticsComponent implements OnInit {
  data: AnalyticsData | null = null;
  loading = true;
  error = '';

  constructor(private promptService: PromptService) {}

  ngOnInit(): void {
    this.promptService.getAnalytics().subscribe({
      next: d => { this.data = d; this.loading = false; },
      error: err => { this.error = err.message; this.loading = false; },
    });
  }

  complexityLabel(n: number): string { return COMPLEXITY_LABELS[n] ?? String(n); }

  get maxCount(): number {
    if (!this.data?.complexity_distribution.length) return 1;
    return Math.max(...this.data.complexity_distribution.map(d => d.count));
  }

  barWidth(count: number): number {
    return Math.round((count / this.maxCount) * 100);
  }

  complexityClass(c: number): string {
    if (c <= 3) return 'easy';
    if (c <= 6) return 'medium';
    if (c <= 8) return 'hard';
    return 'expert';
  }
}
