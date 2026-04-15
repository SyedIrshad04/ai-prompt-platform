import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import {
  ReactiveFormsModule, FormBuilder, FormGroup, Validators,
  FormControl, AbstractControl, ValidationErrors,
} from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { PromptService } from '../../services/prompt.service';
import { Tag } from '../../models/prompt.model';

@Component({
  selector: 'app-prompt-create',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './prompt-create.component.html',
  styleUrls: ['./prompt-create.component.scss'],
})
export class PromptCreateComponent implements OnInit, OnDestroy {
  form: FormGroup;
  availableTags: Tag[] = [];
  selectedTags: string[] = [];
  newTag = '';
  submitting = false;
  error = '';

  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private promptService: PromptService,
    private router: Router,
  ) {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(255)]],
      content: ['', [Validators.required, Validators.minLength(20)]],
      complexity: [5, [Validators.required, Validators.min(1), Validators.max(10)]],
    });
  }

  ngOnInit(): void {
    this.promptService.getTags().pipe(takeUntil(this.destroy$))
      .subscribe({ next: res => this.availableTags = res.results, error: () => {} });
  }

  get f() { return this.form.controls; }

  get complexityValue(): number { return this.form.get('complexity')?.value ?? 5; }

  get complexityLabel(): string {
    const labels: Record<number, string> = {
      1:'Trivial',2:'Simple',3:'Easy',4:'Moderate',5:'Average',
      6:'Involved',7:'Complex',8:'Hard',9:'Expert',10:'Master',
    };
    return labels[this.complexityValue] ?? '';
  }

  get complexityClass(): string {
    const c = this.complexityValue;
    if (c <= 3) return 'easy';
    if (c <= 6) return 'medium';
    if (c <= 8) return 'hard';
    return 'expert';
  }

  toggleTag(tag: string): void {
    const idx = this.selectedTags.indexOf(tag);
    if (idx >= 0) this.selectedTags.splice(idx, 1);
    else if (this.selectedTags.length < 10) this.selectedTags.push(tag);
  }

  addCustomTag(): void {
    const tag = this.newTag.trim().toLowerCase();
    if (!tag || this.selectedTags.includes(tag) || this.selectedTags.length >= 10) return;
    this.selectedTags.push(tag);
    this.newTag = '';
  }

  removeTag(tag: string): void {
    this.selectedTags = this.selectedTags.filter(t => t !== tag);
  }

  onTagKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') { e.preventDefault(); this.addCustomTag(); }
  }

  get contentLength(): number { return this.form.get('content')?.value?.length ?? 0; }

  submit(): void {
    if (this.form.invalid || this.submitting) return;
    this.submitting = true;
    this.error = '';

    const { title, content, complexity } = this.form.value;
    this.promptService.createPrompt({ title, content, complexity, tags: this.selectedTags })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: p => this.router.navigate(['/prompts', p.id]),
        error: err => { this.error = err.message || 'Failed to create prompt.'; this.submitting = false; },
      });
  }

  fieldError(name: string): string {
    const ctrl = this.form.get(name);
    if (!ctrl || !ctrl.touched || !ctrl.errors) return '';
    if (ctrl.errors['required']) return 'This field is required.';
    if (ctrl.errors['minlength']) return `Minimum ${ctrl.errors['minlength'].requiredLength} characters.`;
    if (ctrl.errors['maxlength']) return `Maximum ${ctrl.errors['maxlength'].requiredLength} characters.`;
    if (ctrl.errors['min']) return `Minimum value is ${ctrl.errors['min'].min}.`;
    if (ctrl.errors['max']) return `Maximum value is ${ctrl.errors['max'].max}.`;
    return 'Invalid value.';
  }

  ngOnDestroy(): void { this.destroy$.next(); this.destroy$.complete(); }
}
