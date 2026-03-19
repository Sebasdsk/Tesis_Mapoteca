import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import {
  UsuarioService,
  Usuario,
  UsuarioCreate,
  UsuarioUpdate,
} from '../../core/service/usuario';

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [FormsModule, NgClass],
  templateUrl: './usuarios.html',
  styleUrl: './usuarios.css',
})
export default class UsuariosComponent implements OnInit {
  private usuarioService = inject(UsuarioService);

  usuarios = signal<Usuario[]>([]);
  isLoading = signal(true);
  errorMessage = signal('');

  // Filtros
  tipoFilter = '';
  activoFilter = '';

  // Modal crear/editar
  showModal = signal(false);
  isEditing = signal(false);
  editingId = '';
  formData: UsuarioCreate & { email?: string } = {
    tipo_usuario: 'ESTUDIANTE',
    numero_identificacion: '',
    nombre_completo: '',
    email: '',
    institucion: '',
  };
  formError = signal('');
  formLoading = signal(false);

  // Modal password temporal
  showPasswordModal = signal(false);
  tempPassword = signal('');
  tempPasswordUser = signal('');

  // Confirm action
  showConfirmModal = signal(false);
  confirmAction = signal<(() => void) | null>(null);
  confirmMessage = signal('');

  tiposUsuario = [
    { value: 'ESTUDIANTE', label: 'Estudiante' },
    { value: 'MAESTRO', label: 'Maestro' },
    { value: 'ADMIN', label: 'Administrador' },
    { value: 'EXTERNO', label: 'Externo' },
  ];

  ngOnInit() {
    this.loadUsuarios();
  }

  onFilterChange() {
    this.loadUsuarios();
  }

  // --- Modal Crear/Editar ---

  openCreateModal() {
    this.isEditing.set(false);
    this.editingId = '';
    this.formData = {
      tipo_usuario: 'ESTUDIANTE',
      numero_identificacion: '',
      nombre_completo: '',
      email: '',
      institucion: '',
    };
    this.formError.set('');
    this.showModal.set(true);
  }

  openEditModal(user: Usuario) {
    this.isEditing.set(true);
    this.editingId = user.id;
    this.formData = {
      tipo_usuario: user.tipo_usuario,
      numero_identificacion: user.numero_identificacion || '',
      nombre_completo: user.nombre_completo,
      email: user.email || '',
      institucion: user.institucion || '',
    };
    this.formError.set('');
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
  }

  submitForm() {
    this.formError.set('');
    this.formLoading.set(true);

    if (this.isEditing()) {
      const update: UsuarioUpdate = {
        nombre_completo: this.formData.nombre_completo,
        email: this.formData.email || undefined,
        institucion: this.formData.institucion || undefined,
      };
      this.usuarioService.updateUsuario(this.editingId, update).subscribe({
        next: () => {
          this.formLoading.set(false);
          this.showModal.set(false);
          this.loadUsuarios();
        },
        error: (err) => {
          this.formLoading.set(false);
          this.formError.set(err.error?.detail || 'Error al actualizar usuario');
        },
      });
    } else {
      const create: UsuarioCreate = {
        tipo_usuario: this.formData.tipo_usuario,
        nombre_completo: this.formData.nombre_completo,
        numero_identificacion: this.formData.numero_identificacion || undefined,
        email: this.formData.email || undefined,
        institucion: this.formData.institucion || undefined,
      };
      this.usuarioService.createUsuario(create).subscribe({
        next: (res) => {
          this.formLoading.set(false);
          this.showModal.set(false);
          this.tempPassword.set(res.password_temporal);
          this.tempPasswordUser.set(res.nombre_completo);
          this.showPasswordModal.set(true);
          this.loadUsuarios();
        },
        error: (err) => {
          this.formLoading.set(false);
          this.formError.set(err.error?.detail || 'Error al crear usuario');
        },
      });
    }
  }

  // --- Acciones ---

  toggleActivo(user: Usuario) {
    if (user.activo) {
      this.confirmMessage.set(`¿Desactivar a ${user.nombre_completo}?`);
      this.confirmAction.set(() => {
        this.usuarioService.deactivateUsuario(user.id).subscribe({
          next: () => this.loadUsuarios(),
          error: (err) => this.errorMessage.set(err.error?.detail || 'Error'),
        });
      });
    } else {
      this.confirmMessage.set(`¿Reactivar a ${user.nombre_completo}?`);
      this.confirmAction.set(() => {
        this.usuarioService.activateUsuario(user.id).subscribe({
          next: () => this.loadUsuarios(),
          error: (err) => this.errorMessage.set(err.error?.detail || 'Error'),
        });
      });
    }
    this.showConfirmModal.set(true);
  }

  resetPassword(user: Usuario) {
    this.confirmMessage.set(`¿Resetear la contraseña de ${user.nombre_completo}?`);
    this.confirmAction.set(() => {
      this.usuarioService.resetPassword(user.id).subscribe({
        next: (res) => {
          this.tempPassword.set(res.password_temporal);
          this.tempPasswordUser.set(user.nombre_completo);
          this.showPasswordModal.set(true);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error'),
      });
    });
    this.showConfirmModal.set(true);
  }

  executeConfirm() {
    const action = this.confirmAction();
    if (action) action();
    this.showConfirmModal.set(false);
  }

  cancelConfirm() {
    this.showConfirmModal.set(false);
  }

  closePasswordModal() {
    this.showPasswordModal.set(false);
  }

  getTipoLabel(tipo: string): string {
    return this.tiposUsuario.find((t) => t.value === tipo)?.label || tipo;
  }

  private loadUsuarios() {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const filters: any = {};
    if (this.tipoFilter) filters.tipo_usuario = this.tipoFilter;
    if (this.activoFilter !== '') filters.activo = this.activoFilter === 'true';

    this.usuarioService.getUsuarios(filters).subscribe({
      next: (data) => {
        this.usuarios.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(
          err.status === 401
            ? 'Sesión expirada.'
            : 'Error al cargar usuarios.'
        );
        this.isLoading.set(false);
      },
    });
  }
}
