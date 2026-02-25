import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/service/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink], // Importante para formularios y links
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <h2>Mapoteca Digital</h2>
        <p class="subtitle">Ingresa tus credenciales</p>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" formControlName="email" placeholder="usuario@uas.edu.mx" />
          </div>

          <div class="form-group">
            <label>Contraseña (Prueba con: 123456)</label>
            <input type="password" formControlName="password" />
          </div>

          @if (errorMessage()) {
            <div class="error-banner">
              {{ errorMessage() }}
            </div>
          }

          <button type="submit" [disabled]="loginForm.invalid || isLoading()">
            @if (isLoading()) {
              <span>Procesando...</span>
            } @else {
              <span>Iniciar Sesión</span>
            }
          </button>
        </form>

        <div class="auth-footer">
          <p>¿No tienes cuenta? <a routerLink="/register">Regístrate</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      .auth-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #f4f4f9;
      }
      .auth-card {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 400px;
      }
      .form-group {
        margin-bottom: 1rem;
      }
      label {
        display: block;
        margin-bottom: 0.5rem;
        color: #555;
      }
      input {
        width: 100%;
        padding: 0.8rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
      }
      button {
        width: 100%;
        padding: 1rem;
        background-color: #004a98;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
      }
      button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
      }
      .error-banner {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
      }
      .auth-footer {
        margin-top: 1.5rem;
        text-align: center;
        font-size: 0.9rem;
      }
    `,
  ],
})
export default class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  isLoading = signal(false);
  errorMessage = signal('');

  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    this.errorMessage.set('');

    const { email, password } = this.loginForm.getRawValue();

    this.authService.login({ email, password }).subscribe({
      next: () => {
        // Login exitoso
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.errorMessage.set(err.message); // Mostrará "Credenciales inválidas"
        this.isLoading.set(false);
      },
    });
  }
}
