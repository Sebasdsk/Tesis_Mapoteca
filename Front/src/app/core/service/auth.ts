import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpBackend, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import {
  LoginRequest,
  LoginResponse,
  TokenUser,
  PasswordChangeRequest,
  PasswordChangeResponse,
} from '../models/auth';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private httpBackend = inject(HttpBackend);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  // Cliente que NO pasa por los interceptores. Se usa para login/refresh/logout
  // y así evitar recursión (el interceptor reintenta con refresh) y
  // dependencias circulares de DI.
  private rawHttp = new HttpClient(this.httpBackend);

  // Estado reactivo (el access token vive solo en memoria, no en localStorage)
  private _currentUser = signal<TokenUser | null>(null);
  private _accessToken = signal<string | null>(null);

  public currentUser = this._currentUser.asReadonly();
  public isLoggedIn = computed(() => !!this._accessToken());
  public isAdmin = computed(() => this._currentUser()?.tipo_usuario === 'ADMIN');
  public mustChangePassword = computed(
    () => this._currentUser()?.debe_cambiar_password ?? false
  );

  /**
   * POST /auth/login
   * Guarda el access token en memoria; el refresh token llega en cookie httpOnly.
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.rawHttp
      .post<LoginResponse>(`${this.apiUrl}/auth/login`, credentials, {
        withCredentials: true,
      })
      .pipe(
        tap((response) => this._setSession(response)),
        catchError((error: HttpErrorResponse) => {
          const message =
            error.error?.detail || 'Error al iniciar sesión. Intenta de nuevo.';
          return throwError(() => new Error(message));
        })
      );
  }

  /**
   * POST /auth/refresh
   * Usa la cookie httpOnly para obtener un nuevo access token.
   */
  refresh(): Observable<LoginResponse> {
    return this.rawHttp
      .post<LoginResponse>(
        `${this.apiUrl}/auth/refresh`,
        {},
        { withCredentials: true }
      )
      .pipe(tap((response) => this._setSession(response)));
  }

  /**
   * Restaura la sesión al cargar la app (llamado por APP_INITIALIZER).
   * Si no hay cookie válida, simplemente queda como usuario anónimo.
   */
  initialize(): Observable<void> {
    return this.refresh().pipe(
      map(() => void 0),
      catchError(() => {
        this._clearSession();
        return of(void 0);
      })
    );
  }

  /**
   * POST /auth/change-password
   */
  changePassword(
    data: PasswordChangeRequest
  ): Observable<PasswordChangeResponse> {
    return this.http
      .post<PasswordChangeResponse>(
        `${this.apiUrl}/auth/change-password`,
        data
      )
      .pipe(
        tap((response) => {
          const user = this._currentUser();
          if (user) {
            this._currentUser.set({
              ...user,
              debe_cambiar_password: response.debe_cambiar_password,
            });
          }
        }),
        catchError((error: HttpErrorResponse) => {
          const message =
            error.error?.detail || 'Error al cambiar la contraseña.';
          return throwError(() => new Error(message));
        })
      );
  }

  /**
   * POST /auth/logout y limpieza local.
   */
  logout(): void {
    this.rawHttp
      .post(`${this.apiUrl}/auth/logout`, {}, { withCredentials: true })
      .subscribe({
        next: () => this._afterLogout(),
        error: () => this._afterLogout(),
      });
  }

  /**
   * Retorna el access token actual (usado por el interceptor).
   */
  getToken(): string | null {
    return this._accessToken();
  }

  /** Indica si hay sesión activa (token en memoria). */
  isAuthenticated(): boolean {
    return !!this._accessToken();
  }

  // --- Métodos privados ---

  private _setSession(response: LoginResponse): void {
    this._accessToken.set(response.access_token);
    this._currentUser.set(response.user);
  }

  private _clearSession(): void {
    this._accessToken.set(null);
    this._currentUser.set(null);
  }

  private _afterLogout(): void {
    this._clearSession();
    this.router.navigate(['/login']);
  }
}
