import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ReporteGeneral,
  CartaEstadistica,
  PrestamoVencido,
  PrestamoActivo,
  DistribucionUsuarios,
  ActividadMensual,
} from '../models/reporte';

@Injectable({
  providedIn: 'root',
})
export class ReporteService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/reportes`;

  getReporteGeneral(): Observable<ReporteGeneral> {
    return this.http.get<ReporteGeneral>(`${this.apiUrl}/general`);
  }

  getCartasMasBuscadas(limit = 5): Observable<CartaEstadistica[]> {
    return this.http.get<CartaEstadistica[]>(
      `${this.apiUrl}/cartas-mas-buscadas`,
      { params: { limit } }
    );
  }

  getCartasMasPrestadas(limit = 5): Observable<CartaEstadistica[]> {
    return this.http.get<CartaEstadistica[]>(
      `${this.apiUrl}/cartas-mas-prestadas`,
      { params: { limit } }
    );
  }

  getPrestamosVencidos(): Observable<PrestamoVencido[]> {
    return this.http.get<PrestamoVencido[]>(`${this.apiUrl}/prestamos-vencidos`);
  }

  getPrestamosActivos(): Observable<PrestamoActivo[]> {
    return this.http.get<PrestamoActivo[]>(`${this.apiUrl}/prestamos-activos`);
  }

  getDistribucionUsuarios(): Observable<DistribucionUsuarios[]> {
    return this.http.get<DistribucionUsuarios[]>(`${this.apiUrl}/distribucion-usuarios`);
  }

  getActividadMensual(meses = 12): Observable<ActividadMensual[]> {
    return this.http.get<ActividadMensual[]>(
      `${this.apiUrl}/actividad-mensual`,
      { params: { meses } }
    );
  }
}
