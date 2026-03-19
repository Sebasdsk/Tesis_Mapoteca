import { Routes } from '@angular/router';
import { authGuard, passwordChangedGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  // Rutas públicas
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login'),
  },
  {
    path: 'cambiar-password',
    loadComponent: () =>
      import('./features/auth/cambiar-password/cambiar-password'),
  },

  // Rutas protegidas (dentro del layout)
  {
    path: '',
    loadComponent: () => import('./layout/layout'),
    canActivate: [authGuard, passwordChangedGuard],
    children: [
      // Catálogo
      {
        path: 'catalogo',
        loadComponent: () => import('./features/catalogo/catalogo'),
      },
      {
        path: 'catalogo/nuevo',
        loadComponent: () =>
          import('./features/catalogo/carta-form/carta-form'),
      },
      {
        path: 'catalogo/:id',
        loadComponent: () =>
          import('./features/catalogo/carta-detalle/carta-detalle'),
      },
      {
        path: 'catalogo/:id/editar',
        loadComponent: () =>
          import('./features/catalogo/carta-form/carta-form'),
      },

      // Usuarios (admin)
      {
        path: 'usuarios',
        loadComponent: () => import('./features/usuarios/usuarios'),
      },

      // Placeholders
      {
        path: 'prestamos',
        loadComponent: () => import('./features/catalogo/catalogo'), // placeholder
      },
      {
        path: 'reportes',
        loadComponent: () => import('./features/catalogo/catalogo'), // placeholder
      },

      // Redirect vacío → catálogo
      {
        path: '',
        redirectTo: 'catalogo',
        pathMatch: 'full',
      },
    ],
  },

  // Wildcard → Login
  {
    path: '**',
    redirectTo: 'login',
  },
];
