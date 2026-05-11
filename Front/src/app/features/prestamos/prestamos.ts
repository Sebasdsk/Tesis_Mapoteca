import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PrestamoService } from '../../core/service/prestamo';
import { AuthService } from '../../core/service/auth';
import {
  Prestamo,
  EstadoPrestamo,
  EvaluacionEstado,
  PrestamoFilters,
} from '../../core/models/prestamo';

@Component({
  selector: 'app-prestamos',
  standalone: true,
  imports: [FormsModule, NgClass, RouterLink],
  templateUrl: './prestamos.html',
  styleUrl: './prestamos.css',
})
export default class PrestamosComponent implements OnInit {
  private prestamoService = inject(PrestamoService);
  authService = inject(AuthService);

  prestamos = signal<Prestamo[]>([]);
  isLoading = signal(true);
  errorMessage = signal('');
  successMessage = signal('');

  // Filtros
  estadoFilter = '';

  // Paginación
  currentPage = signal(0);
  pageSize = 20;
  hasMore = signal(false);

  // --- Modales ---

  // Modal Aprobar
  showAprobarModal = signal(false);
  aprobarPrestamoId = '';
  aprobarFechaLimite = '';
  aprobarNotasAdmin = '';
  aprobarLoading = signal(false);

  // Modal Rechazar
  showRechazarModal = signal(false);
  rechazarPrestamoId = '';
  rechazarMotivo = '';
  rechazarLoading = signal(false);

  // Modal Entregar
  showEntregarModal = signal(false);
  entregarPrestamoId = '';
  entregarNotas = '';
  entregarLoading = signal(false);

  // Modal Devolver
  showDevolverModal = signal(false);
  devolverPrestamoId = '';
  devolverEvaluacion: EvaluacionEstado = 'BUENO';
  devolverNotas = '';
  devolverLoading = signal(false);

  // Modal Detalle
  showDetalleModal = signal(false);
  detallePrestamo = signal<Prestamo | null>(null);

  // Confirm modal genérico
  showConfirmModal = signal(false);
  confirmMessage = signal('');
  confirmAction = signal<(() => void) | null>(null);

  // Catálogos
  estados: { value: EstadoPrestamo; label: string }[] = [
    { value: 'SOLICITADO', label: 'Solicitado' },
    { value: 'APROBADO', label: 'Aprobado' },
    { value: 'RECHAZADO', label: 'Rechazado' },
    { value: 'ENTREGADO', label: 'Entregado' },
    { value: 'DEVUELTO', label: 'Devuelto' },
    { value: 'VENCIDO', label: 'Vencido' },
  ];

  ngOnInit() {
    this.loadPrestamos();
  }

  onFilterChange() {
    this.currentPage.set(0);
    this.loadPrestamos();
  }

  nextPage() {
    this.currentPage.update((p) => p + 1);
    this.loadPrestamos();
  }

  prevPage() {
    this.currentPage.update((p) => Math.max(0, p - 1));
    this.loadPrestamos();
  }

  // --- Helpers de display ---

  getEstadoLabel(estado: string): string {
    return this.estados.find((e) => e.value === estado)?.label || estado;
  }

  getEstadoClasses(estado: string): Record<string, boolean> {
    return {
      'badge-solicitado': estado === 'SOLICITADO',
      'badge-aprobado': estado === 'APROBADO',
      'badge-rechazado': estado === 'RECHAZADO',
      'badge-entregado': estado === 'ENTREGADO',
      'badge-devuelto': estado === 'DEVUELTO',
      'badge-vencido': estado === 'VENCIDO',
    };
  }

  getEvaluacionLabel(eval_estado: string | null): string {
    if (!eval_estado) return '—';
    const map: Record<string, string> = {
      BUENO: 'Bueno',
      REGULAR: 'Regular',
      MALO: 'Malo',
    };
    return map[eval_estado] || eval_estado;
  }

  formatDate(dateStr: string | null): string {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-MX', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  formatDateTime(dateStr: string | null): string {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-MX', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  getDefaultFechaLimite(): string {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  }

  // --- Ver detalle ---

  openDetalle(prestamo: Prestamo) {
    this.detallePrestamo.set(prestamo);
    this.showDetalleModal.set(true);
  }

  closeDetalle() {
    this.showDetalleModal.set(false);
  }

  // --- Aprobar ---

  openAprobarModal(prestamo: Prestamo) {
    this.aprobarPrestamoId = prestamo.id;
    this.aprobarFechaLimite = this.getDefaultFechaLimite();
    this.aprobarNotasAdmin = '';
    this.errorMessage.set('');
    this.showAprobarModal.set(true);
  }

  closeAprobarModal() {
    this.showAprobarModal.set(false);
  }

  submitAprobar() {
    if (!this.aprobarFechaLimite) return;
    this.aprobarLoading.set(true);

    this.prestamoService
      .aprobarPrestamo(this.aprobarPrestamoId, {
        fecha_limite: this.aprobarFechaLimite,
        notas_admin: this.aprobarNotasAdmin || undefined,
      })
      .subscribe({
        next: () => {
          this.aprobarLoading.set(false);
          this.showAprobarModal.set(false);
          this.showSuccess('Préstamo aprobado correctamente');
          this.loadPrestamos();
        },
        error: (err) => {
          this.aprobarLoading.set(false);
          this.errorMessage.set(
            err.error?.detail || 'Error al aprobar préstamo'
          );
        },
      });
  }

  // --- Rechazar ---

  openRechazarModal(prestamo: Prestamo) {
    this.rechazarPrestamoId = prestamo.id;
    this.rechazarMotivo = '';
    this.errorMessage.set('');
    this.showRechazarModal.set(true);
  }

  closeRechazarModal() {
    this.showRechazarModal.set(false);
  }

  submitRechazar() {
    if (!this.rechazarMotivo.trim()) return;
    this.rechazarLoading.set(true);

    this.prestamoService
      .rechazarPrestamo(this.rechazarPrestamoId, {
        motivo_rechazo: this.rechazarMotivo.trim(),
      })
      .subscribe({
        next: () => {
          this.rechazarLoading.set(false);
          this.showRechazarModal.set(false);
          this.showSuccess('Préstamo rechazado');
          this.loadPrestamos();
        },
        error: (err) => {
          this.rechazarLoading.set(false);
          this.errorMessage.set(
            err.error?.detail || 'Error al rechazar préstamo'
          );
        },
      });
  }

  // --- Entregar ---

  openEntregarModal(prestamo: Prestamo) {
    this.entregarPrestamoId = prestamo.id;
    this.entregarNotas = '';
    this.errorMessage.set('');
    this.showEntregarModal.set(true);
  }

  closeEntregarModal() {
    this.showEntregarModal.set(false);
  }

  submitEntregar() {
    this.entregarLoading.set(true);

    this.prestamoService
      .entregarPrestamo(this.entregarPrestamoId, {
        notas_admin: this.entregarNotas || undefined,
      })
      .subscribe({
        next: () => {
          this.entregarLoading.set(false);
          this.showEntregarModal.set(false);
          this.showSuccess('Entrega registrada correctamente');
          this.loadPrestamos();
        },
        error: (err) => {
          this.entregarLoading.set(false);
          this.errorMessage.set(
            err.error?.detail || 'Error al registrar entrega'
          );
        },
      });
  }

  // --- Devolver ---

  openDevolverModal(prestamo: Prestamo) {
    this.devolverPrestamoId = prestamo.id;
    this.devolverEvaluacion = 'BUENO';
    this.devolverNotas = '';
    this.errorMessage.set('');
    this.showDevolverModal.set(true);
  }

  closeDevolverModal() {
    this.showDevolverModal.set(false);
  }

  submitDevolver() {
    this.devolverLoading.set(true);

    this.prestamoService
      .devolverPrestamo(this.devolverPrestamoId, {
        evaluacion_estado: this.devolverEvaluacion,
        evaluacion_notas: this.devolverNotas || undefined,
      })
      .subscribe({
        next: () => {
          this.devolverLoading.set(false);
          this.showDevolverModal.set(false);
          this.showSuccess('Devolución registrada correctamente');
          this.loadPrestamos();
        },
        error: (err) => {
          this.devolverLoading.set(false);
          this.errorMessage.set(
            err.error?.detail || 'Error al registrar devolución'
          );
        },
      });
  }

  // --- Utils ---

  private showSuccess(msg: string) {
    this.successMessage.set(msg);
    setTimeout(() => this.successMessage.set(''), 4000);
  }

  private loadPrestamos() {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const filters: PrestamoFilters = {
      skip: this.currentPage() * this.pageSize,
      limit: this.pageSize + 1,
    };

    if (this.estadoFilter) {
      filters.estado = this.estadoFilter as EstadoPrestamo;
    }

    this.prestamoService.getPrestamos(filters).subscribe({
      next: (data) => {
        if (data.length > this.pageSize) {
          this.hasMore.set(true);
          this.prestamos.set(data.slice(0, this.pageSize));
        } else {
          this.hasMore.set(false);
          this.prestamos.set(data);
        }
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(
          err.status === 401
            ? 'Sesión expirada. Inicia sesión nuevamente.'
            : 'Error al cargar préstamos. Verifica que el servidor esté activo.'
        );
        this.isLoading.set(false);
      },
    });
  }
}
