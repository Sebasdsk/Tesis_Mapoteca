import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { RolUsuario, User } from '../../../core/models/auth';
import { AuthService } from '../../../core/service/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <h2>Crear Cuenta</h2>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label>Nombre Completo</label>
            <input type="text" formControlName="fullName" />
          </div>

          <div class="form-group">
            <label>Correo Institucional</label>
            <input type="email" formControlName="email" />
          </div>

          <div class="form-group">
            <label>Tipo de Usuario</label>
            <select formControlName="role">
              <option value="" disabled>Selecciona...</option>
              @for (role of roles; track role) {
                <option [value]="role">{{ role }}</option>
              }
            </select>
          </div>

          <div class="form-group">
            <label>Contraseña</label>
            <input type="password" formControlName="password" />
          </div>

          <button type="submit" [disabled]="registerForm.invalid || isLoading()">
            @if (isLoading()) {
              Registrando...
            } @else {
              Registrarse
            }
          </button>
        </form>

        <div class="auth-footer">
          <p>¿Ya tienes cuenta? <a routerLink="/login">Inicia Sesión</a></p>
        </div>
      </div>
    </div>
  `,
  // Reutilizamos los estilos del Login (podrías ponerlos en un styles.css global)
  styles: [
    `
      /* Pega aquí los mismos estilos del Login o impórtalos */
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
      input,
      select {
        width: 100%;
        padding: 0.8rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
      }
      button {
        width: 100%;
        padding: 1rem;
        background-color: #28a745;
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
      .auth-footer {
        margin-top: 1.5rem;
        text-align: center;
      }
    `,
  ],
})
export default class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  isLoading = signal(false);
  roles: RolUsuario[] = ['Estudiante', 'Profesor', 'Externo'];

  registerForm = this.fb.nonNullable.group({
    Nombre: ['', Validators.required],
    Apellido: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    rol: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  onSubmit() {
    if (this.registerForm.invalid) return;

    this.isLoading.set(true);
    const formValue = this.registerForm.getRawValue();

    this.authService.register(formValue).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: () => this.isLoading.set(false),
    });
  }
}
