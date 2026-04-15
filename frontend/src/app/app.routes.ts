import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'prompts', pathMatch: 'full' },
  {
    path: 'prompts',
    loadComponent: () =>
      import('./features/prompts/components/prompt-list/prompt-list.component')
        .then(m => m.PromptListComponent),
  },
  {
    path: 'prompts/create',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/prompts/components/prompt-create/prompt-create.component')
        .then(m => m.PromptCreateComponent),
  },
  {
    path: 'prompts/:id',
    loadComponent: () =>
      import('./features/prompts/components/prompt-detail/prompt-detail.component')
        .then(m => m.PromptDetailComponent),
  },
  {
    path: 'analytics',
    loadComponent: () =>
      import('./analytics/analytics.component').then(m => m.AnalyticsComponent),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./login/login.component').then(m => m.LoginComponent),
  },
  { path: '**', redirectTo: 'prompts' },
];
