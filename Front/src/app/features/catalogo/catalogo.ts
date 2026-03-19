import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { CartaService, CartaFilters } from '../../core/service/carta';
import { CartaSimple } from '../../core/models/carta';

@Component({
  selector: 'app-catalogo',
  standalone: true,
  imports: [RouterLink, FormsModule, NgClass],
  templateUrl: './catalogo.html',
  styleUrl: './catalogo.css',
})
export default class CatalogoComponent implements OnInit, OnDestroy {
  private cartaService = inject(CartaService);
  private destroy$ = new Subject<void>();
  private searchSubject$ = new Subject<string>();

  cartas = signal<CartaSimple[]>([]);
  isLoading = signal(true);
  errorMessage = signal('');

  // Filtros
  searchTerm = '';
  tipoCartaFilter = '';
  disponibilidadFilter = '';
  escalaFilter = '';

  // Paginación
  currentPage = signal(0);
  pageSize = 12;
  hasMore = signal(false);

  // Catálogos para filtros
  tiposCarta = [
    { value: 'TOPOGRAFICA', label: 'Topográfica' },
    { value: 'GEOLOGICA', label: 'Geológica' },
    { value: 'HIDROLOGICA', label: 'Hidrológica' },
    { value: 'EDAFOLOGICA', label: 'Edafológica' },
    { value: 'USO_SUELO', label: 'Uso de Suelo' },
    { value: 'CLIMATICA', label: 'Climática' },
    { value: 'OTRA', label: 'Otra' },
  ];

  disponibilidades = [
    { value: 'FISICA', label: 'Física' },
    { value: 'SOLO_DIGITAL', label: 'Solo Digital' },
    { value: 'AMBAS', label: 'Física + Digital' },
    { value: 'EXTRAVIADA', label: 'Extraviada' },
    { value: 'DANADA', label: 'Dañada' },
  ];

  escalas = [
    { value: '1:50,000', label: '1:50,000' },
    { value: '1:250,000', label: '1:250,000' },
    { value: '1:1,000,000', label: '1:1,000,000' },
  ];

  ngOnInit() {
    // Debounce de búsqueda
    this.searchSubject$
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe((term) => {
        this.searchTerm = term;
        this.currentPage.set(0);
        this.loadCartas();
      });

    this.loadCartas();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSearchInput(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.searchSubject$.next(value);
  }

  onFilterChange() {
    this.currentPage.set(0);
    this.loadCartas();
  }

  clearFilters() {
    this.searchTerm = '';
    this.tipoCartaFilter = '';
    this.disponibilidadFilter = '';
    this.escalaFilter = '';
    this.currentPage.set(0);
    this.loadCartas();
  }

  nextPage() {
    this.currentPage.update((p) => p + 1);
    this.loadCartas();
  }

  prevPage() {
    this.currentPage.update((p) => Math.max(0, p - 1));
    this.loadCartas();
  }

  getDisponibilidadClass(disponibilidad: string): string {
    switch (disponibilidad) {
      case 'FISICA':
      case 'AMBAS':
        return 'badge-disponible';
      case 'SOLO_DIGITAL':
        return 'badge-digital';
      case 'EXTRAVIADA':
      case 'DANADA':
        return 'badge-no-disponible';
      default:
        return 'badge-default';
    }
  }

  getDisponibilidadLabel(disponibilidad: string): string {
    switch (disponibilidad) {
      case 'FISICA':
        return 'Física';
      case 'SOLO_DIGITAL':
        return 'Solo Digital';
      case 'AMBAS':
        return 'Física + Digital';
      case 'EXTRAVIADA':
        return 'Extraviada';
      case 'DANADA':
        return 'Dañada';
      default:
        return disponibilidad;
    }
  }

  getTipoLabel(tipo: string): string {
    return this.tiposCarta.find((t) => t.value === tipo)?.label || tipo;
  }

  private loadCartas() {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const filters: CartaFilters = {
      skip: this.currentPage() * this.pageSize,
      limit: this.pageSize + 1, // +1 to detect if there are more
    };

    if (this.searchTerm) filters.search = this.searchTerm;
    if (this.tipoCartaFilter) filters.tipo_carta = this.tipoCartaFilter;
    if (this.disponibilidadFilter) filters.disponibilidad = this.disponibilidadFilter;
    if (this.escalaFilter) filters.escala = this.escalaFilter;

    this.cartaService.getCartas(filters).subscribe({
      next: (data) => {
        if (data.length > this.pageSize) {
          this.hasMore.set(true);
          this.cartas.set(data.slice(0, this.pageSize));
        } else {
          this.hasMore.set(false);
          this.cartas.set(data);
        }
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(
          err.status === 401
            ? 'Sesión expirada. Inicia sesión nuevamente.'
            : 'Error al cargar el catálogo. Verifica que el servidor esté activo.'
        );
        this.isLoading.set(false);
      },
    });
  }
}
