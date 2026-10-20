import { Component, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { FuenteInegiService } from '../../core/service/fuente-inegi';
import { CartaService } from '../../core/service/carta';
import { ToastService } from '../../core/service/toast';
import { FuenteInegi } from '../../core/models/fuente-inegi';
import { TipoCarta } from '../../core/models/carta';

function urlInegi(control: AbstractControl): ValidationErrors | null {
  const valor = String(control.value || '').trim();
  if (!valor) return null;
  try {
    const url = new URL(valor);
    const oficial = url.hostname === 'inegi.org.mx' || url.hostname.endsWith('.inegi.org.mx');
    return url.protocol === 'https:' && oficial && !url.username && !url.password &&
      (!url.port || url.port === '443') && !/\s/.test(valor) ? null : { urlInegi: true };
  } catch {
    return { urlInegi: true };
  }
}

@Component({
  selector: 'app-fuentes-inegi',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './fuentes-inegi.html',
})
export default class FuentesInegiComponent {
  private servicio = inject(FuenteInegiService);
  private cartas = inject(CartaService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);
  private destroyRef = inject(DestroyRef);

  fuentes = signal<FuenteInegi[]>([]);
  escalas = signal<string[]>([]);
  cargando = signal(true);
  error = signal('');
  mostrarFormulario = signal(false);
  editandoId = signal<string | null>(null);
  guardando = signal(false);
  errorFormulario = signal('');
  pendienteEliminar = signal<FuenteInegi | null>(null);
  eliminando = signal(false);
  errorEliminar = signal('');

  tipos: { value: TipoCarta; label: string }[] = [
    { value: 'TOPOGRAFICA', label: 'Topográfica' },
    { value: 'GEOLOGICA', label: 'Geológica' },
    { value: 'HIDROLOGICA', label: 'Hidrológica' },
    { value: 'EDAFOLOGICA', label: 'Edafológica' },
    { value: 'USO_SUELO', label: 'Uso de suelo' },
    { value: 'CLIMATICA', label: 'Climática' },
    { value: 'OTRA', label: 'Otra' },
  ];

  formulario = this.fb.nonNullable.group({
    escala: ['', [Validators.required, Validators.maxLength(50), Validators.pattern(/^1:[0-9][0-9,]*$/)]],
    tipo_carta: this.fb.nonNullable.control<TipoCarta>('TOPOGRAFICA'),
    nombre: ['', [Validators.required, Validators.maxLength(150)]],
    url: ['', [Validators.required, urlInegi]],
  });

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set('');
    forkJoin({ fuentes: this.servicio.listar(), escalas: this.cartas.getEscalas() })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ fuentes, escalas }) => {
          this.fuentes.set(fuentes);
          this.escalas.set([...new Set([...escalas, ...fuentes.map(f => f.escala)])].sort());
          this.cargando.set(false);
        },
        error: (err: HttpErrorResponse) => {
          this.error.set(this.mensajeError(err, 'No se pudieron cargar las fuentes INEGI.'));
          this.cargando.set(false);
        },
      });
  }

  abrirFormulario(fuente?: FuenteInegi): void {
    this.errorFormulario.set('');
    this.editandoId.set(fuente?.id ?? null);
    this.formulario.reset(fuente ? {
      escala: fuente.escala, tipo_carta: fuente.tipo_carta, nombre: fuente.nombre, url: fuente.url,
    } : { escala: '', tipo_carta: 'TOPOGRAFICA', nombre: '', url: '' });
    this.mostrarFormulario.set(true);
  }

  guardar(): void {
    if (this.guardando()) return;
    this.formulario.markAllAsTouched();
    if (this.formulario.invalid) return;
    const valores = this.formulario.getRawValue();
    const datos = { ...valores, escala: valores.escala.trim(), nombre: valores.nombre.trim(), url: valores.url.trim() };
    if (!datos.nombre) {
      this.errorFormulario.set('Escribe un nombre para la fuente.');
      return;
    }
    this.guardando.set(true);
    this.errorFormulario.set('');
    const id = this.editandoId();
    const operacion = id ? this.servicio.editar(id, datos) : this.servicio.crear(datos);
    operacion.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.guardando.set(false);
        this.mostrarFormulario.set(false);
        this.toast.success(id ? 'Fuente INEGI actualizada' : 'Fuente INEGI registrada');
        this.cargar();
      },
      error: (err: HttpErrorResponse) => {
        this.guardando.set(false);
        this.errorFormulario.set(this.mensajeError(err, 'No se pudo guardar la fuente.'));
      },
    });
  }

  confirmarEliminar(fuente: FuenteInegi): void {
    this.errorEliminar.set('');
    this.pendienteEliminar.set(fuente);
  }

  eliminar(): void {
    const fuente = this.pendienteEliminar();
    if (!fuente || this.eliminando()) return;
    this.eliminando.set(true);
    this.errorEliminar.set('');
    this.servicio.eliminar(fuente.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.eliminando.set(false);
        this.pendienteEliminar.set(null);
        this.toast.success('Fuente INEGI eliminada');
        this.cargar();
      },
      error: (err: HttpErrorResponse) => {
        this.eliminando.set(false);
        this.errorEliminar.set(this.mensajeError(err, 'No se pudo eliminar la fuente.'));
      },
    });
  }

  tipoLabel(tipo: TipoCarta): string {
    return this.tipos.find(t => t.value === tipo)?.label ?? tipo;
  }

  private mensajeError(err: HttpErrorResponse, defecto: string): string {
    if (err.status === 0) return 'No se pudo conectar con el servidor. Revisa tu conexión e intenta de nuevo.';
    if (typeof err.error?.detail === 'string') return err.error.detail;
    if (Array.isArray(err.error?.detail)) {
      return err.error.detail.map((detalle: { msg: string }) => detalle.msg).join('. ');
    }
    return defecto;
  }
}
