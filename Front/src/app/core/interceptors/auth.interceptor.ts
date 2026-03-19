import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../service/auth';

/**
 * Interceptor funcional que agrega el header Authorization con el JWT
 * a todas las peticiones HTTP salientes y maneja errores 401.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Obtener token actual
  const token = authService.getToken();

  // Clonar request con header de autorización si hay token
  const authReq = token
    ? req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
        },
      })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si el servidor responde 401, cerrar sesión y redirigir a login
      if (error.status === 401) {
        authService.logout();
      }
      return throwError(() => error);
    })
  );
};
