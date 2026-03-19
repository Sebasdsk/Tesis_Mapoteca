import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import {
  LoginRequest,
  LoginResponse,
  TokenUser,
  PasswordChangeRequest,
  PasswordChangeResponse,
} from '../models/auth';
import { environment } from '../../../environments/environment';

const TOKEN_KEY = 'mapoteca_token';
const USER_KEY = 'mapoteca_user';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  // Estado reactivo
  private _currentUser = signal<TokenUser | null>(this._getUserFromStorage());
  private _token = signal<string | null>(this._getTokenFromStorage());

  // Selectores públicos (readonly)
  public currentUser = this._currentUser.asReadonly();
  public isLoggedIn = computed(() => !!this._token());
  public isAdmin = computed(
    () => this._currentUser()?.tipo_usuario === 'ADMIN'
  );
  public mustChangePassword = computed(
    () => this._currentUser()?.debe_cambiar_password ?? false
  );

  /**
   * POST /auth/login
   * Autentica al usuario y guarda el token JWT
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          this._saveSession(response.access_token, response.user);
        }),
        catchError((error: HttpErrorResponse) => {
          const message =
            error.error?.detail || 'Error al iniciar sesión. Intenta de nuevo.';
          return throwError(() => new Error(message));
        })
      );
  }

  /**
   * POST /auth/change-password
   * Cambia la contraseña del usuario actual
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
          // Actualizar el flag debe_cambiar_password en el estado local
          const user = this._currentUser();
          if (user) {
            const updatedUser: TokenUser = {
              ...user,
              debe_cambiar_password: response.debe_cambiar_password,
            };
            this._currentUser.set(updatedUser);
            localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
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
   * GET /auth/me
   * Obtiene la información del usuario actual
   */
  getMe(): Observable<TokenUser> {
    return this.http.get<TokenUser>(`${this.apiUrl}/auth/me`).pipe(
      tap((user) => {
        this._currentUser.set(user);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      })
    );
  }

  /**
   * Cierra sesión: limpia token y usuario del estado y localStorage
   */
  logout(): void {
    this._token.set(null);
    this._currentUser.set(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.router.navigate(['/login']);
  }

  /**
   * Retorna el token actual (usado por el interceptor)
   */
  getToken(): string | null {
    return this._token();
  }

  // --- Métodos privados ---

  private _saveSession(token: string, user: TokenUser): void {
    this._token.set(token);
    this._currentUser.set(user);
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  private _getTokenFromStorage(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  private _getUserFromStorage(): TokenUser | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as TokenUser;
    } catch {
      return null;
    }
  }
}
