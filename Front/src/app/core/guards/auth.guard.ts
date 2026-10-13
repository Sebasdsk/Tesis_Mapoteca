import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../service/auth';

/**
 * Guard que protege rutas requiriendo autenticación.
 * Redirige a /login si el usuario no tiene un token válido.
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
};

/**
 * Guard que verifica si el usuario debe cambiar su contraseña.
 * Si debe_cambiar_password = true, redirige a /cambiar-password.
 * Usar en rutas que NO sean /cambiar-password ni /login.
 */
export const passwordChangedGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.mustChangePassword()) {
    router.navigate(['/cambiar-password']);
    return false;
  }

  return true;
};

/**
 * Guard que restringe el acceso a rutas de administrador.
 * Redirige a /login si no hay sesión y a /catalogo si no es ADMIN.
 */
export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    router.navigate(['/login']);
    return false;
  }

  if (!authService.isAdmin()) {
    router.navigate(['/catalogo']);
    return false;
  }

  return true;
};

/**
 * Guard para gestión del catálogo (ADMIN o MAESTRO).
 * Redirige a /login si no hay sesión y a /catalogo si no tiene permiso.
 */
export const managerGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    router.navigate(['/login']);
    return false;
  }

  if (!authService.canManageCatalog()) {
    router.navigate(['/catalogo']);
    return false;
  }

  return true;
};
