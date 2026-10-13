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
  total = signal(0);
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

  escalas: string[] = [];

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
    this.cartaService.getEscalas().subscribe({
      next: (escalas) => (this.escalas = escalas),
      error: () => {},
    });
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
      limit: this.pageSize,
    };

    if (this.searchTerm) filters.search = this.searchTerm;
    if (this.tipoCartaFilter) filters.tipo_carta = this.tipoCartaFilter;
    if (this.disponibilidadFilter) filters.disponibilidad = this.disponibilidadFilter;
    if (this.escalaFilter) filters.escala = this.escalaFilter;

    this.cartaService.getCartas(filters).subscribe({
      next: ({ items, total }) => {
        this.cartas.set(items);
        this.total.set(total);
        this.hasMore.set(this.currentPage() * this.pageSize + items.length < total);
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
