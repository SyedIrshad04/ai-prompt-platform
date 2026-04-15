import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, switchMap, takeUntil, startWith, combineLatest } from 'rxjs';
import { PromptService } from '../../services/prompt.service';
import { Prompt, PromptListResponse } from '../../models/prompt.model';
import { PromptCardComponent } from '../prompt-card/prompt-card.component';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-prompt-list',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, PromptCardComponent],
  templateUrl: './prompt-list.component.html',
  styleUrls: ['./prompt-list.component.scss'],
})
export class PromptListComponent implements OnInit, OnDestroy {
  prompts: Prompt[] = [];
  total = 0;
  totalPages = 0;
  currentPage = 1;
  pageSize = 9;
  loading = false;
  error = '';

  filterForm: FormGroup;
  isLoggedIn = false;

  complexityOptions = [1,2,3,4,5,6,7,8,9,10];
  sortOptions = [
    { value: '-created_at', label: 'Newest first' },
    { value: 'created_at',  label: 'Oldest first' },
    { value: '-complexity', label: 'Complexity ↓' },
    { value: 'complexity',  label: 'Complexity ↑' },
    { value: 'title',       label: 'Title A–Z' },
    { value: '-title',      label: 'Title Z–A' },
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private promptService: PromptService,
    private auth: AuthService,
    private fb: FormBuilder,
  ) {
    this.filterForm = this.fb.group({
      search:     [''],
      complexity: [null],
      sort:       ['-created_at'],
    });
  }

  ngOnInit(): void {
    this.auth.isLoggedIn$.pipe(takeUntil(this.destroy$))
      .subscribe(v => this.isLoggedIn = v);

    this.filterForm.valueChanges.pipe(
      debounceTime(350),
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      takeUntil(this.destroy$),
    ).subscribe(() => {
      this.currentPage = 1;
      this.loadPrompts();
    });

    this.loadPrompts();
  }

  loadPrompts(): void {
    this.loading = true;
    this.error = '';
    const { search, complexity, sort } = this.filterForm.value;

    this.promptService.getPrompts({
      search: search || undefined,
      complexity: complexity || undefined,
      sort,
      page: this.currentPage,
      page_size: this.pageSize,
    }).pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (res: PromptListResponse) => {
          this.prompts = res.results;
          this.total = res.total;
          this.totalPages = res.total_pages;
          this.loading = false;
        },
        error: (err) => {
          this.error = err.message || 'Failed to load prompts.';
          this.loading = false;
        },
      });
  }

  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.loadPrompts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  clearFilters(): void {
    this.filterForm.reset({ search: '', complexity: null, sort: '-created_at' });
    this.currentPage = 1;
  }

  get pages(): number[] {
    const total = this.totalPages;
    const cur = this.currentPage;
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages: number[] = [];
    if (cur <= 4) {
      pages.push(...[1,2,3,4,5], -1, total);
    } else if (cur >= total - 3) {
      pages.push(1, -1, ...Array.from({ length: 5 }, (_, i) => total - 4 + i));
    } else {
      pages.push(1, -1, cur - 1, cur, cur + 1, -1, total);
    }
    return pages;
  }

  get hasActiveFilters(): boolean {
    const { search, complexity } = this.filterForm.value;
    return !!(search || complexity);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
