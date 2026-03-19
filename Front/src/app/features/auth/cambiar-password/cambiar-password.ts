import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/service/auth';

@Component({
  selector: 'app-cambiar-password',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './cambiar-password.html',
  styleUrl: './cambiar-password.css',
})
export default class CambiarPasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  isLoading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  passwordForm = this.fb.nonNullable.group(
    {
      current_password: ['', [Validators.required]],
      new_password: ['', [Validators.required, Validators.minLength(8), this.passwordStrength]],
      confirm_password: ['', [Validators.required]],
    },
    { validators: this.passwordsMatch }
  );

  /** Validador: la contraseña debe tener mayúscula, minúscula y número */
  passwordStrength(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const hasUpper = /[A-Z]/.test(value);
    const hasLower = /[a-z]/.test(value);
    const hasDigit = /[0-9]/.test(value);

    if (!hasUpper || !hasLower || !hasDigit) {
      return { passwordStrength: true };
    }
    return null;
  }

  /** Validador de grupo: las contraseñas deben coincidir */
  passwordsMatch(group: AbstractControl): ValidationErrors | null {
    const newPass = group.get('new_password')?.value;
    const confirm = group.get('confirm_password')?.value;

    if (newPass && confirm && newPass !== confirm) {
      return { passwordsMismatch: true };
    }
    return null;
  }

  // Helpers para indicadores de fuerza en el template
  hasMinLength(): boolean {
    return (this.passwordForm.get('new_password')?.value?.length ?? 0) >= 8;
  }

  hasUppercase(): boolean {
    return /[A-Z]/.test(this.passwordForm.get('new_password')?.value || '');
  }

  hasLowercase(): boolean {
    return /[a-z]/.test(this.passwordForm.get('new_password')?.value || '');
  }

  hasDigit(): boolean {
    return /[0-9]/.test(this.passwordForm.get('new_password')?.value || '');
  }

  onSubmit() {
    if (this.passwordForm.invalid) return;

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    const formData = this.passwordForm.getRawValue();

    this.authService.changePassword(formData).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.successMessage.set('¡Contraseña actualizada correctamente!');

        // Redirigir después de 1.5 segundos
        setTimeout(() => {
          // TODO: Cambiar a /catalogo o /admin/dashboard según rol
          this.router.navigate(['/login']);
        }, 1500);
      },
      error: (err: Error) => {
        this.errorMessage.set(err.message);
        this.isLoading.set(false);
      },
    });
  }
}
