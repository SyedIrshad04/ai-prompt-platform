import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Prompt, COMPLEXITY_LABELS } from '../../models/prompt.model';

@Component({
  selector: 'app-prompt-card',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './prompt-card.component.html',
  styleUrls: ['./prompt-card.component.scss'],
})
export class PromptCardComponent {
  @Input() prompt!: Prompt;

  get complexityLabel(): string {
    return COMPLEXITY_LABELS[this.prompt.complexity] ?? 'Unknown';
  }

  get complexityClass(): string {
    const c = this.prompt.complexity;
    if (c <= 3) return 'badge--easy';
    if (c <= 6) return 'badge--medium';
    if (c <= 8) return 'badge--hard';
    return 'badge--expert';
  }

  get preview(): string {
    return this.prompt.content.length > 140
      ? this.prompt.content.slice(0, 140) + '…'
      : this.prompt.content;
  }

  get formattedDate(): string {
    return new Date(this.prompt.created_at).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    });
  }
}
