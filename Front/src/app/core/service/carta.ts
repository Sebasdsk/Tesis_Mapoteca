import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Carta, CartaSimple } from '../models/carta';
import { environment } from '../../../environments/environment';

export interface CartaFilters {
  search?: string;
  tipo_carta?: string;
  disponibilidad?: string;
  escala?: string;
  estado_republica?: string;
  skip?: number;
  limit?: number;
}

@Injectable({ providedIn: 'root' })
export class CartaService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/cartas`;

  /**
   * GET /cartas — Lista con filtros opcionales
   */
  getCartas(filters: CartaFilters = {}): Observable<CartaSimple[]> {
    let params = new HttpParams();

    if (filters.search) params = params.set('search', filters.search);
    if (filters.tipo_carta) params = params.set('tipo_carta', filters.tipo_carta);
    if (filters.disponibilidad) params = params.set('disponibilidad', filters.disponibilidad);
    if (filters.escala) params = params.set('escala', filters.escala);
    if (filters.estado_republica) params = params.set('estado_republica', filters.estado_republica);
    if (filters.skip != null) params = params.set('skip', filters.skip.toString());
    if (filters.limit != null) params = params.set('limit', filters.limit.toString());

    return this.http.get<CartaSimple[]>(this.apiUrl, { params });
  }

  /**
   * GET /cartas/:id — Detalle completo
   */
  getCarta(id: string): Observable<Carta> {
    return this.http.get<Carta>(`${this.apiUrl}/${id}`);
  }

  /**
   * POST /cartas — Crear carta (admin)
   */
  createCarta(carta: Partial<Carta>): Observable<Carta> {
    return this.http.post<Carta>(this.apiUrl, carta);
  }

  /**
   * PUT /cartas/:id — Actualizar carta (admin)
   */
  updateCarta(id: string, carta: Partial<Carta>): Observable<Carta> {
    return this.http.put<Carta>(`${this.apiUrl}/${id}`, carta);
  }

  /**
   * DELETE /cartas/:id — Eliminar carta (admin)
   */
  deleteCarta(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
