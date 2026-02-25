import { Injectable, signal, computed } from '@angular/core';
import { User, RolUsuario } from '../models/auth';
import { Observable, of, throwError } from 'rxjs';
import { delay, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  // ESTADO: Signal para guardar el usuario actual
  private _currentUser = signal<User | null>(this._getUserFromStorage());

  // SELECTORES: Para leer el estado desde los componentes
  public currentUser = this._currentUser.asReadonly();
  public isAuthenticated = computed(() => !!this._currentUser());

  // MOCK LOGIN: Simula una petición al servidor
  login(credentials: { email: string; password: string }): Observable<User> {
    // Simulamos un usuario falso que devuelve el "backend"
    const mockUser: User = {
      id: '1',
      Nombre: 'Sebastian',
      Apellido: 'Villa', // Basado en tu tesis
      email: credentials.email,
      rol: 'Estudiante',
    };

    // Simulamos validación simple
    if (credentials.password === '123456') {
      return of(mockUser).pipe(
        delay(1000), // Simula 1 segundo de retraso de red
        tap((user) => {
          this._currentUser.set(user);
          this._saveToStorage(user);
        }),
      );
    } else {
      // Simula error de contraseña
      return throwError(() => new Error('Credenciales inválidas')).pipe(delay(1000));
    }
  }

  // MOCK REGISTER
  register(userData: any): Observable<User> {
    const newUser: User = {
      id: Math.random().toString(36).substr(2, 9),
      Nombre: userData.Nombre,
      Apellido: userData.Apellido,
      email: userData.email,
      rol: userData.rol,
    };

    return of(newUser).pipe(
      delay(1500), // El registro suele tardar un poco más
      tap((user) => {
        this._currentUser.set(user);
        this._saveToStorage(user);
      }),
    );
  }

  logout() {
    this._currentUser.set(null);
    localStorage.removeItem('mapoteca_user');
  }

  // Persistencia local para que no se cierre sesión al recargar
  private _saveToStorage(user: User) {
    localStorage.setItem('mapoteca_user', JSON.stringify(user));
  }

  private _getUserFromStorage(): User | null {
    const userStr = localStorage.getItem('mapoteca_user');
    return userStr ? JSON.parse(userStr) : null;
  }
}
