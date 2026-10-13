import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../service/auth';

/**
 * Interceptor funcional que:
 *  - agrega el header Authorization con el access token (en memoria)
 *  - envía cookies (withCredentials) para el refresh token httpOnly
 *  - ante un 401, intenta refrescar la sesión una vez y reintenta la petición
 *  - ante un 403, propaga el error (p. ej. sin permisos o debe cambiar password)
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  const token = auth.getToken();
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

  const authReq = req.clone({ setHeaders: headers ?? {}, withCredentials: true });

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Intentar renovar el access token y reintentar una sola vez.
        return auth.refresh().pipe(
          switchMap((response) => {
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${response.access_token}` },
              withCredentials: true,
            });
            return next(retryReq);
          }),
          catchError(() => {
            auth.logout();
            return throwError(() => error);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
