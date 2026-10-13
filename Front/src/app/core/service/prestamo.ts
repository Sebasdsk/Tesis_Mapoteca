import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  Prestamo,
  PrestamoSolicitar,
  PrestamoDirecto,
  PrestamoAprobar,
  PrestamoRechazar,
  PrestamoEntregar,
  PrestamoDevolver,
  PrestamoFilters,
} from '../models/prestamo';
import { Paginated } from './carta';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PrestamoService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/prestamos`;

  /**
   * GET /prestamos — Lista con filtros opcionales.
   * Admin ve todos, usuarios normales solo los suyos.
   * El total (sin paginar) llega en el header X-Total-Count.
   */
  getPrestamos(filters: PrestamoFilters = {}): Observable<Paginated<Prestamo>> {
    let params = new HttpParams();

    if (filters.estado) params = params.set('estado', filters.estado);
    if (filters.usuario_id) params = params.set('usuario_id', filters.usuario_id);
    if (filters.carta_id) params = params.set('carta_id', filters.carta_id);
    if (filters.skip != null) params = params.set('skip', filters.skip.toString());
    if (filters.limit != null) params = params.set('limit', filters.limit.toString());

    return this.http
      .get<Prestamo[]>(this.apiUrl, { params, observe: 'response' })
      .pipe(
        map((res) => ({
          items: res.body ?? [],
          total: Number(res.headers.get('X-Total-Count') ?? res.body?.length ?? 0),
        }))
      );
  }

  /**
   * GET /prestamos/:id — Detalle de un préstamo
   */
  getPrestamo(id: string): Observable<Prestamo> {
    return this.http.get<Prestamo>(`${this.apiUrl}/${id}`);
  }

  /**
   * POST /prestamos — CU-08: Solicitar préstamo
   */
  solicitarPrestamo(data: PrestamoSolicitar): Observable<Prestamo> {
    return this.http.post<Prestamo>(this.apiUrl, data);
  }

  /**
   * POST /prestamos/directo — Préstamo presencial (ADMIN/MAESTRO)
   * Crea el préstamo ya en estado ENTREGADO y deja la carta ocupada.
   */
  registrarPrestamoDirecto(data: PrestamoDirecto): Observable<Prestamo> {
    return this.http.post<Prestamo>(`${this.apiUrl}/directo`, data);
  }

  /**
   * POST /prestamos/:id/aprobar — CU-09: Aprobar solicitud (admin)
   */
  aprobarPrestamo(id: string, data: PrestamoAprobar): Observable<Prestamo> {
    return this.http.post<Prestamo>(`${this.apiUrl}/${id}/aprobar`, data);
  }

  /**
   * POST /prestamos/:id/rechazar — CU-09: Rechazar solicitud (admin)
   */
  rechazarPrestamo(id: string, data: PrestamoRechazar): Observable<Prestamo> {
    return this.http.post<Prestamo>(`${this.apiUrl}/${id}/rechazar`, data);
  }

  /**
   * POST /prestamos/:id/entregar — CU-09: Registrar entrega (admin)
   */
  entregarPrestamo(id: string, data: PrestamoEntregar): Observable<Prestamo> {
    return this.http.post<Prestamo>(`${this.apiUrl}/${id}/entregar`, data);
  }

  /**
   * POST /prestamos/:id/devolver — CU-10: Registrar devolución (admin)
   */
  devolverPrestamo(id: string, data: PrestamoDevolver): Observable<Prestamo> {
    return this.http.post<Prestamo>(`${this.apiUrl}/${id}/devolver`, data);
  }
}
