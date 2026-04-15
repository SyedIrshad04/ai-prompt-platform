import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { PromptService } from '../../services/prompt.service';
import { AuthService } from '../../../../core/services/auth.service';
import { Prompt, COMPLEXITY_LABELS } from '../../models/prompt.model';

@Component({
  selector: 'app-prompt-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './prompt-detail.component.html',
  styleUrls: ['./prompt-detail.component.scss'],
})
export class PromptDetailComponent implements OnInit, OnDestroy {
  prompt: Prompt | null = null;
  loading = true;
  error = '';
  deleting = false;
  isLoggedIn = false;
  copied = false;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private promptService: PromptService,
    private auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.auth.isLoggedIn$.pipe(takeUntil(this.destroy$))
      .subscribe(v => this.isLoggedIn = v);

    this.route.paramMap.pipe(takeUntil(this.destroy$)).subscribe(params => {
      const id = params.get('id');
      if (id) this.loadPrompt(id);
    });
  }

  loadPrompt(id: string): void {
    this.loading = true;
    this.error = '';
    this.promptService.getPrompt(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: p => { this.prompt = p; this.loading = false; },
        error: err => {
          this.error = err.message || 'Prompt not found.';
          this.loading = false;
        },
      });
  }

  deletePrompt(): void {
    if (!this.prompt || !confirm('Delete this prompt?')) return;
    this.deleting = true;
    this.promptService.deletePrompt(this.prompt.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => this.router.navigate(['/prompts']),
        error: err => { this.error = err.message; this.deleting = false; },
      });
  }

  copyContent(): void {
    if (!this.prompt) return;
    navigator.clipboard.writeText(this.prompt.content).then(() => {
      this.copied = true;
      setTimeout(() => this.copied = false, 2000);
    });
  }

  get complexityLabel(): string {
    return this.prompt ? (COMPLEXITY_LABELS[this.prompt.complexity] ?? '') : '';
  }

  get complexityClass(): string {
    const c = this.prompt?.complexity ?? 0;
    if (c <= 3) return 'badge--easy';
    if (c <= 6) return 'badge--medium';
    if (c <= 8) return 'badge--hard';
    return 'badge--expert';
  }

  get formattedDate(): string {
    if (!this.prompt) return '';
    return new Date(this.prompt.created_at).toLocaleDateString('en-US', {
      month: 'long', day: 'numeric', year: 'numeric',
    });
  }

  ngOnDestroy(): void { this.destroy$.next(); this.destroy$.complete(); }
}
