import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { FuenteInegi, FuenteInegiDatos } from '../models/fuente-inegi';

@Injectable({ providedIn: 'root' })
export class FuenteInegiService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/fuentes-inegi`;

  listar(): Observable<FuenteInegi[]> {
    return this.http.get<FuenteInegi[]>(`${this.apiUrl}/`);
  }

  crear(datos: FuenteInegiDatos): Observable<FuenteInegi> {
    return this.http.post<FuenteInegi>(`${this.apiUrl}/`, datos);
  }

  editar(id: string, datos: FuenteInegiDatos): Observable<FuenteInegi> {
    return this.http.put<FuenteInegi>(`${this.apiUrl}/${id}`, datos);
  }

  eliminar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
