import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login'),
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register'),
  },
  // Redirección por defecto
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
  // Placeholder para cuando te loguees
  {
    path: 'dashboard',
    loadComponent: () => import('./features/auth/login/login'), // Temporal: redirige al login visualmente
  },
];
