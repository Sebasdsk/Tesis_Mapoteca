import { Routes } from '@angular/router';
import { authGuard, passwordChangedGuard, adminGuard, managerGuard } from './core/guards/auth.guard';

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
        canActivate: [managerGuard],
      },
      {
        path: 'catalogo/carga-masiva',
        loadComponent: () =>
          import('./features/catalogo/carga-masiva/carga-masiva'),
        canActivate: [managerGuard],
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
        canActivate: [managerGuard],
      },

      // Usuarios (admin)
      {
        path: 'usuarios',
        loadComponent: () => import('./features/usuarios/usuarios'),
        canActivate: [adminGuard],
      },

      // Préstamos
      {
        path: 'prestamos',
        loadComponent: () => import('./features/prestamos/prestamos'),
      },
      {
        path: 'reportes',
        loadComponent: () => import('./features/reportes/reportes'),
        canActivate: [adminGuard],
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
